# -*- coding: utf-8 -*-
# ToMaTo (Topology management software) 
# Copyright (C) 2010 Dennis Schwerdel, University of Kaiserslautern
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os, sys
from django.db import models
from tomato import connections, elements, resources, host, fault
from tomato.resources import template
from tomato.lib.attributes import attribute, between
from tomato.lib import util
from tomato.host import fileserver

DOC="""
Element type: repy

Description:
	This element type provides programming language virtualization by using the
	Repy python sandbox. An adapted version of the original Seattle Repy that
	can read and write ethernet packets is used.

Possible parents: None

Possible children:
	repy_interface (can be added in state created)

Default state: created

Removable in states: created

Connection concepts: None

States:
	created: In this state the program is known of and the script exists.
		Only the script is stored and no othe resources are consumed in this
		state.
	started: In this state the program is running and can be accessed by the
		user. The program holds a memory state but no disk state. It consumes
		memory, cpu power, io and networking resources.
		
Attributes:
	args: list, changeable in state created, default: []
		The arguments to pass to the program when it is started.
	cpus: float, changeable in state created, default: 0.25
		The number of processors that the program can use. This can be set to a
		fraction to limit the program to that fraction of the processor. If 
		this value is greater than 1.0 the program is allowed to use the 
		resources of more than one processor using several threads.
	ram: int, changeable in state created, default: 25
		The amount of memory the program should have in megabytes. The program
		will only be able to use this much memory for its data structures. If
		the program tries to use more, this will result in exceptions and/or
		the program being terminated.
	bandwidth: int, changeable in state created, default: 1000000
		The amount of traffic that the program is allowed to cause in bytes per
		second. All the incoming and the outgoing traffic of all interface is
		counted against this value but the limit is applied seperately for 
		incoming and outgoing traffic. The limit is only applied on a per 
		second basis, i.e. short bursts can go over this limit.
	template: str, changeable in state created
		The name of a template of matching virtualization technology to be used
		for this program. A copy of this template will be used as the script 
		for this program. If no template with the given name exists (esp. for
		template=None), a default template is chosen instead.
	vncport: int, read-only
		The port on this host on which the VM can be accessed via VNC when it
		is running. 
	vncpassword: int, read-only
		The random password that has to be used to connect to this VM using 
		VNC. This password should be kept secret.

Actions:
	start, callable in state created, next state: started
	 	Starts the program and runs the script, and starts a VNC server that
	 	displays the output of the script. This action also connects all the
	 	interfaces of the device.
	stop, callable in state started, next state: created
	 	Stops the VNC server and then stops the program.
	upload_grant, callable in state created
	 	Create/update a grant to upload an image for the VM. The created grant
	 	will be available as an attribute called upload_grant. The grant allows
	 	the user to upload a file for a certain time. The url where the file 
	 	must be uploaded has the form http://server:port/grant/upload where
	 	server is the address of this host, port is the fileserver port of this
	 	server (can be requested via host_info) and grant is the grant.
	 	The uploaded file can be used as the VM image with the upload_use 
	 	action. 
	upload_use, callable in state created
		Uses a previously uploaded file as the image of the VM. 
	download_grant, callable in state created
	 	Create/update a grant to download the image for the VM. The created 
	 	grant will be available as an attribute called download_grant. The
	 	grant allows the user to download the VM image once for a certain time.
	 	The url where the file can be downloaded from has the form 
	 	http://server:port/grant/download where server is the address of this
	 	host, port is the fileserver port of this server (can be requested via
	 	host_info) and grant is the grant.
"""


class Repy(elements.Element):
	pid = attribute("pid", int)
	vncport = attribute("vncport", int)
	vncpid = attribute("vncpid", int)
	vncpassword = attribute("vncpassword", str)
	upload_grant = attribute("upload_grant", str)
	download_grant = attribute("download_grant", str)
	args = attribute("args", list, default=[])
	cpus = attribute("cpus", between(0.01, 4.0, faultType=fault.new_user), default=0.25)
	ram = attribute("ram", between(10, 4096, faultType=fault.new_user), default=25)
	bandwidth = attribute("bandwidth", between(1024, 10000000000, faultType=fault.new_user), default=1000000)
	template = models.ForeignKey(template.Template, null=True)

	ST_CREATED = "created"
	ST_STARTED = "started"
	TYPE = "repy"
	CAP_ACTIONS = {
		"start": [ST_CREATED],
		"stop": [ST_STARTED],
		"upload_grant": [ST_CREATED],
		"upload_use": [ST_CREATED],
		"download_grant": [ST_CREATED],
		"__remove__": [ST_CREATED],
	}
	CAP_NEXT_STATE = {
		"start": ST_STARTED,
		"stop": ST_CREATED,
	}	
	CAP_ATTRS = {
		"template": [ST_CREATED],
		"args": [ST_CREATED],
		"cpus": [ST_CREATED],
		"ram": [ST_CREATED],
		"bandwidth": [ST_CREATED],
	}
	CAP_CHILDREN = {
		"repy_interface": [ST_CREATED],
	}
	CAP_PARENT = [None]
	DEFAULT_ATTRS = {"args": [], "cpus": 0.25, "ram": 25, "bandwidth": 1000000}
	DOC = DOC
	
	class Meta:
		db_table = "tomato_repy"
		app_label = 'tomato'
	
	def init(self, *args, **kwargs):
		self.type = self.TYPE
		self.state = self.ST_CREATED
		elements.Element.init(self, *args, **kwargs) #no id and no attrs before this line
		self.vmid = self.getResource("vmid")
		self.vncport = self.getResource("port")
		self.vncpassword = host.randomPassword()
		self.modify_template("") #use default template
		self._setProfile()

	def _interfaceName(self, name):
		return "repy%d%s" % (self.id, name)

	def _template(self):
		if self.template:
			return self.template
		pref = resources.template.getPreferred(self.TYPE)
		fault.check(pref, "Failed to find template for %s", self.TYPE, fault.INTERNAL_ERROR)
		return pref
				
	def _nextIfaceName(self):
		ifaces = self.getChildren()
		num = 0
		while "eth%d" % num in [iface.name for iface in ifaces]:
			num += 1
		return "eth%d" % num

	def _useImage(self, path):
		img = host.Path(path)
		img.copyTo(self.dataPath("program.repy"))

	def _setProfile(self):
		res = {"diskused": 1000000, "lograte": 10000, "events": 10000, "random": 10000}
		res.update({"cpu": self.cpus, "memory": self.ram*1000000, "netrecv": self.bandwidth, "netsend": self.bandwidth})
		with open(self.dataPath("resources"), "w") as fp:
			for key, value in res.iteritems():
				fp.write("resource %s %s\n" % (key, value))

	def _checkImage(self, path):
		res = host.run(["repy-check", path]).strip()
		if res != "None":
			import re
			res = re.match("<(type|class) '([^']*)'> (.*)", res)
			fault.check(False, "Repy script error: %s %s", (res.group(2), res.group(3)))

	def modify_cpus(self, val):
		self.cpus = val
		self._setProfile()
	
	def modify_ram(self, val):
		self.ram = val
		self._setProfile()

	def modify_bandwidth(self, val):
		self.bandwidth = val
		self._setProfile()

	def modify_args(self, val):
		self.args = val

	def modify_template(self, tmplName):
		self.template = resources.template.get(self.TYPE, tmplName)
		self._useImage(self._template().getPath())

	def action_start(self):
		iargs = sum((["-i", "%s,alias=%s" % (self._interfaceName(iface.name), iface.name)] for iface in self.getChildren()), [])
		stdout = open(self.dataPath("program.log"), "w")
		self.pid = host.spawn(["tomato-repy", "-p", self.dataPath("program.repy"), "-r", self.dataPath("resources"), "-v"] + iargs + map(host.escape, self.args), stdout=stdout)
		self.setState(self.ST_STARTED, True)
		for interface in self.getChildren():
			ifObj = host.Interface(self._interfaceName(interface.name))
			util.waitFor(ifObj.exists)
			con = interface.getConnection()
			if con:
				con.connectInterface(self._interfaceName(interface.name))
		self.vncpid = host.spawnShell("vncterm -timeout 0 -rfbport %d -passwd %s -c bash -c 'while true; do tail -n +1 -f %s; done'" % (self.vncport, self.vncpassword, self.dataPath("program.log")))				

	def action_stop(self):
		for interface in self.getChildren():
			con = interface.getConnection()
			if con:
				con.disconnectInterface(self._interfaceName(interface.name))
		if self.vncpid:
			host.kill(self.vncpid)
			del self.vncpid
		if self.pid:
			host.kill(self.pid)
			del self.pid
		self.setState(self.ST_CREATED, True)
		
	def action_upload_grant(self):
		self.upload_grant = fileserver.addGrant(self.dataPath("uploaded.repy"), fileserver.ACTION_UPLOAD)
		
	def action_upload_use(self):
		fault.check(os.path.exists(self.dataPath("uploaded.repy")), "No file has been uploaded")
		self._checkImage(self.dataPath("uploaded.repy"))
		os.rename(self.dataPath("uploaded.repy"), self.dataPath("program.repy"))
		
	def action_download_grant(self):
		#no need to copy file first
		self.download_grant = fileserver.addGrant(self.dataPath("program.repy"), fileserver.ACTION_DOWNLOAD)
		
	def upcast(self):
		return self

	def info(self):
		info = elements.Element.info(self)
		info["attrs"]["template"] = self.template.name if self.template else None
		return info


DOC_IFACE="""
Element type: repy_interface

Description:
	This element type represents a network interface of repy element type. Its
	state is managed by and synchronized with the parent element.

Possible parents: repy

Possible children: None

Default state: created

Removable in states: created
	
Connection concepts: interface

States:
	created: In this state the interface is known of.
	started: In this state the interface is running.
		
Attributes: None

Actions: None
"""

class Repy_Interface(elements.Element):
	name = attribute("name", str)

	TYPE = "repy_interface"
	CAP_ACTIONS = {
		"__remove__": [Repy.ST_CREATED]
	}
	CAP_NEXT_STATE = {}
	CAP_ATTRS = {
	}
	CAP_CHILDREN = {}
	CAP_PARENT = [Repy.TYPE]
	CAP_CON_CONCEPTS = [connections.CONCEPT_INTERFACE]
	DOC = DOC_IFACE
	
	class Meta:
		db_table = "tomato_repy_interface"
		app_label = 'tomato'
	
	def init(self, *args, **kwargs):
		self.type = self.TYPE
		self.state = Repy.ST_CREATED
		elements.Element.init(self, *args, **kwargs) #no id and no attrs before this line
		assert isinstance(self.getParent(), Repy)
		self.name = self.getParent()._nextIfaceName()
		
	def interfaceName(self):
		if self.state == Repy.ST_STARTED:
			return self.getParent()._interfaceName(self.name)
		else:
			return None
		
	def upcast(self):
		return self

	def info(self):
		info = elements.Element.info(self)
		return info


repyVersion = host.getDpkgVersion("tomato-repy")
vnctermVersion = host.getDpkgVersion("vncterm")

def register():
	if not repyVersion:
		print >>sys.stderr, "Warning: Repy needs tomato-repy, disabled"
		return
	if not ([0, 5] <= repyVersion):
		print >>sys.stderr, "Warning: Repy not supported on tomato-repy version %s, disabled" % repyVersion
		return
	if not vnctermVersion:
		print >>sys.stderr, "Warning: Repy needs vncterm, disabled"
		return
	elements.TYPES[Repy.TYPE] = Repy
	elements.TYPES[Repy_Interface.TYPE] = Repy_Interface

register()
