from .. import scheduler
from ..lib.error import InternalError, UserError
from ..lib.service import get_tomato_inner_proxy
from ..lib.settings import Config
from ..lib.topology_role import Role
from ..lib.cache import cached

from ..topology import Topology
from ..elements import Element
from ..connections import Connection
from ..host.site import Site
from ..host import Host

import time

class ExistenceCheck(object):
	__slots__ = ("_exists",)

	def __init__(self):
		self._exists = None

	def invalidate_exists(self):
		self._exists = None

	def set_exists(self, exists):
		self._exists = exists

	def exists(self):
		if self._exists is None:
			self._exists = self._check_exists()
		return self._exists

	def _check_exists(self):
		raise InternalError(code=InternalError.UNKNOWN, message="this function should have been overridden", data={'function': '%s.exists' % repr(self.__class__)})

class InfoObj(ExistenceCheck):
	__slots__ = ("_info")

	def __init__(self):
		self._info = None

	def invalidate_info(self):
		self._info = None
		self.invalidate_exists()

	def _fetch_data(self):
		raise InternalError(code=InternalError.UNKNOWN, message="this function should have been overridden", data={'function': '%s._fetch_data' % repr(self.__class__)})

	def info(self):
		if self._info is None:
			self._info = self._fetch_data()
			self.set_exists(True)  # otherwise, fetch_data would have thrown an error
		return self._info


class UserInfo(InfoObj):
	__slots__ = ("name",)

	def __init__(self, username):
		super(UserInfo, self).__init__()
		self.name = username

	def _fetch_data(self):
		return get_tomato_inner_proxy(Config.TOMATO_MODULE_BACKEND_USERS).user_info(self.name)

	def get_username(self):
		return self.name

	def get_flags(self):
		return self.info()['flags']

	def get_organization_name(self):
		return self.info()['organization']

	def _check_exists(self):
		if self._info is not None:
			return True
		return get_tomato_inner_proxy(Config.TOMATO_MODULE_BACKEND_USERS).user_exists(self.name)


class OrganizationInfo(InfoObj):
	__slots__ = ("name",)

	def __init__(self, organization_name):
		super(OrganizationInfo, self).__init__()
		self.name = organization_name

	def _fetch_data(self):
		return get_tomato_inner_proxy(Config.TOMATO_MODULE_BACKEND_USERS).organization_info(self.name)

	def get_organization_name(self):
		return self.get_organization_name()

	def _check_exists(self):
		if self._info is not None:
			return True
		return get_tomato_inner_proxy(Config.TOMATO_MODULE_BACKEND_USERS).organization_exists(self.name)






class TopologyInfo(ExistenceCheck):
	"""
	:type topology: Topology
	"""
	__slots__ = ("topology", "topology_id")

	def __init__(self, topology_id):
		self.topology = Topology.get(topology_id)
		UserError.check(self.topology, code=UserError.ENTITY_DOES_NOT_EXIST, message="Topology with that id does not exist", data={"topology_id": topology_id})
		self.topology_id = topology_id

	def user_has_role(self, username, role):
		"""
		check if the user 'username' has the role 'role'.
		This ignores global or organization-internal permission flags of the given user.
		:param str username: user to check
		:param str role: role as in auth.permissions.Role
		:return: whether the user has this role (or a higher one)
		:rtype: bool
		"""
		return self.topology.user_has_role(username, role)

	def organization_has_role(self, organization, role):
		"""
		check whether the organization has the given role.

		:param str organization: target organization name
		:param str role: maximum role as in auth.permissions.Role
		:return: the role
		:rtype: bool
		"""
		return self.topology.organization_has_role(organization, role)

	def get_id(self):
		"""
		return the topology id of this toppology
		:return:
		"""
		return self.topology_id

	def _check_exists(self):
		# __init__ would throw an error if it didn't exist...
		return True


class SiteInfo(ExistenceCheck):
	__slots__ = ("site",)

	def __init__(self, site_name):
		self.site = Site.objects.get(site_name)
		UserError.check(self.site, code=UserError.ENTITY_DOES_NOT_EXIST, message="Site with that name does not exist", data={"site_name": site_name})

	def get_organization_name(self):
		return self.site.organization

	def _check_exists(self):
		# __init__ would throw an error if it didn't exist...
		return True

class HostInfo(ExistenceCheck):
	__slots__ = ("host",)

	def __init__(self, host_name):
		self.host = Host.objects.get(host_name)
		UserError.check(self.host, code=UserError.ENTITY_DOES_NOT_EXIST, message="Host with that name does not exist", data={"host_name": host_name})

	def get_organization_name(self):
		return self.host.site.organization

	def _check_exists(self):
		# __init__ would throw an error if it didn't exist...
		return True

class ElementInfo(ExistenceCheck):
	__slots__ = ("element",)

	def __init__(self, element_id):
		self.element = Element.get(element_id)
		UserError.check(self.element, code=UserError.ENTITY_DOES_NOT_EXIST, message="Element with that id does not exist", data={"element_id": element_id})

	def get_topology_info(self):
		return get_topology_info(self.element.topology.id)

	def _check_exists(self):
		# __init__ would throw an error if it didn't exist...
		return True

class ConnectionInfo(ExistenceCheck):
	__slots__ = ("connection",)

	def __init__(self, connection_id):
		self.connection = Connection.get(connection_id)
		UserError.check(self.connection, code=UserError.ENTITY_DOES_NOT_EXIST, message="Connection with that id does not exist", data={"connection_id": connection_id})

	def get_topology_info(self):
		return get_topology_info(self.connection.topology.id)

	def _check_exists(self):
		# __init__ would throw an error if it didn't exist...
		return True






def get_connection_info(connection_id):
	"""
	return ConnectionInfo object for the respective topology
	:param connection_id: id of connection
	:return: ConnectionInfo object
	:rtype: ConnectionInfo
	"""
	return ConnectionInfo(connection_id)

def get_element_info(element_id):
	"""
	return ElementInfo object for the respective element
	:param element_id: id of element
	:return: ElementInfo object
	:rtype: ElementInfo
	"""
	return ElementInfo(element_id)


def get_topology_info(topology_id):
	"""
	return TopologyInfo object for the respective topology
	:param topology_id: id of topology
	:return: TopologyInfo object
	:rtype: TopologyInfo
	"""
	return TopologyInfo(topology_id)


def get_site_info(site_name):
	"""
	return SiteInfo object for the respective site
	:param str site_name: name of the target site
	:return: SiteInfo object
	:rtype: SiteInfo
	"""
	return SiteInfo(site_name)


def get_host_info(host_name):
	"""
	return HostInfo object for the respective host
	:param str host_name: name of the target host
	:return: HostInfo object
	:rtype: HostInfo
	"""
	return HostInfo(host_name)

@cached(60)
def get_organization_info(organization_name):
	"""
	return OrganizationInfo object for the respective organization
	:param str organization_name: name of the target organization
	:return: OrganizationInfo object
	:rtype: OrganizationInfo
	"""
	return OrganizationInfo(organization_name)
