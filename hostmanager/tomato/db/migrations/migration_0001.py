
from django.db import models
from ...lib import db, attributes, logging
from ...lib.attributes import Attr
from ...lib.constants import ActionName, StateName, TechName

kblang_options = {"en-us": "English (US)",
					"en-gb": "English (GB)",
					"de": "German",
					"fr": "French",
					"ja": "Japanese"
}

def Connection(db.ChangesetMixin, attributes.Mixin, models.Model):
    type = models.CharField(max_length=20, validators=[db.nameValidator],
                            choices=[(t, t) for t in ["bridge", "fixed_bridge"]])  # @ReservedAssignment
    owner = models.ForeignKey(User, related_name='connections')
    state = models.CharField(max_length=20, validators=[db.nameValidator])
    usageStatistics = models.OneToOneField(UsageStatistics, null=True, related_name='connection')
    attrs = db.JSONField()
    # elements: set of elements.Element


def Bridge(Connection):
    bridge_attr = Attr("bridge", type="str")
    bridge = bridge_attr.attribute()

    emulation_attr = Attr("emulation", desc="Enable emulation", type="bool", default=True)
    emulation = emulation_attr.attribute()

    bandwidth_to_attr = Attr("bandwidth_to", desc="Bandwidth", unit="kbit/s", type="float", minValue=0,
                             maxValue=1000000, default=10000)
    bandwidth_to = bandwidth_to_attr.attribute()
    bandwidth_from_attr = Attr("bandwidth_from", desc="Bandwidth", unit="kbit/s", type="float", minValue=0,
                               maxValue=1000000, default=10000)
    bandwidth_from = bandwidth_from_attr.attribute()

    lossratio_to_attr = Attr("lossratio_to", desc="Loss ratio", unit="%", type="float", minValue=0.0, maxValue=100.0,
                             default=0.0)
    lossratio_to = lossratio_to_attr.attribute()
    lossratio_from_attr = Attr("lossratio_from", desc="Loss ratio", unit="%", type="float", minValue=0.0,
                               maxValue=100.0, default=0.0)
    lossratio_from = lossratio_from_attr.attribute()

    duplicate_to_attr = Attr("duplicate_to", desc="Duplication ratio", unit="%", type="float", minValue=0.0,
                             maxValue=100.0, default=0.0)
    duplicate_to = duplicate_to_attr.attribute()
    duplicate_from_attr = Attr("duplicate_from", desc="Duplication ratio", unit="%", type="float", minValue=0.0,
                               maxValue=100.0, default=0.0)
    duplicate_from = duplicate_from_attr.attribute()

    corrupt_to_attr = Attr("corrupt_to", desc="Corruption ratio", unit="%", type="float", minValue=0.0, maxValue=100.0,
                           default=0.0)
    corrupt_to = corrupt_to_attr.attribute()
    corrupt_from_attr = Attr("corrupt_from", desc="Corruption ratio", unit="%", type="float", minValue=0.0,
                             maxValue=100.0, default=0.0)
    corrupt_from = corrupt_from_attr.attribute()

    delay_to_attr = Attr("delay_to", desc="Delay", unit="ms", type="float", minValue=0.0, default=0.0)
    delay_to = delay_to_attr.attribute()
    delay_from_attr = Attr("delay_from", desc="Delay", unit="ms", type="float", minValue=0.0, default=0.0)
    delay_from = delay_from_attr.attribute()

    jitter_to_attr = Attr("jitter_to", desc="Jitter", unit="ms", type="float", minValue=0.0, default=0.0)
    jitter_to = jitter_to_attr.attribute()
    jitter_from_attr = Attr("jitter_from", desc="Jitter", unit="ms", type="float", minValue=0.0, default=0.0)
    jitter_from = jitter_from_attr.attribute()

    distribution_to_attr = Attr("distribution_to", desc="Distribution", type="str",
                                options={"uniform": "Uniform", "normal": "Normal", "pareto": "Pareto",
                                         "paretonormal": "Pareto-Normal"}, default="uniform")
    distribution_to = distribution_to_attr.attribute()
    distribution_from_attr = Attr("distribution_from", desc="Distribution", type="str",
                                  options={"uniform": "Uniform", "normal": "Normal", "pareto": "Pareto",
                                           "paretonormal": "Pareto-Normal"}, default="uniform")
    distribution_from = distribution_from_attr.attribute()

    capturing_attr = Attr("capturing", desc="Enable packet capturing", type="bool", default=False)
    capturing = capturing_attr.attribute()
    capture_filter_attr = Attr("capture_filter", desc="Packet filter expression", type="str", default="")
    capture_filter = capture_filter_attr.attribute()
    capture_port_attr = Attr("capture_port", type="int")
    capture_port = capture_port_attr.attribute()
    capture_mode_attr = Attr("capture_mode", desc="Capture mode", type="str",
                             options={"net": "Via network", "file": "For download"}, default="file")
    capture_mode = capture_mode_attr.attribute()
    capture_pid_attr = Attr("capture_pid", type="int")
    capture_pid = capture_pid_attr.attribute()

    TYPE = "bridge"

class Fixed_Bridge(Connection):
    TYPE = "fixed_bridge"

class Element(db.ChangesetMixin, attributes.Mixin, models.Model):
	type = models.CharField(max_length=20, validators=[db.nameValidator],
		choices=[(t, t) for t in TYPES.keys()])  # @ReservedAssignment
	owner = models.ForeignKey(User, related_name='elements')
	parent = models.ForeignKey('self', null=True, related_name='children')
	connection = models.ForeignKey(Connection, null=True, related_name='elements')
	usageStatistics = models.OneToOneField(UsageStatistics, null=True, related_name='element')
	state = models.CharField(max_length=20, validators=[db.nameValidator])
	timeout = models.FloatField()
	timeout_attr = Attr("timeout", desc="Timeout", states=[], type="float", null=False)
    attrs = db.JSONField()

class RexTFVElement:
    rextfv_max_size = None

class External_Network(Element):
	network_attr = Attr("network", null=True)
    network = models.ForeignKey(Network, null=True, related_name="instances")

class KVM(RexTFVElement,Element):
	vmid_attr = Attr("vmid", type="int")
	vmid = vmid_attr.attribute()
	websocket_port_attr = Attr("websocket_port", type="int")
	websocket_port = websocket_port_attr.attribute()
	websocket_pid_attr = Attr("websocket_pid", type="int")
	websocket_pid = websocket_pid_attr.attribute()
	vncport_attr = Attr("vncport", type="int")
	vncport = vncport_attr.attribute()
	vncpid_attr = Attr("vncpid", type="int")
	vncpid = vncpid_attr.attribute()
	vncpassword_attr = Attr("vncpassword", type="str")
	vncpassword = vncpassword_attr.attribute()
	cpus_attr = Attr("cpus", desc="Number of CPUs", states=[StateName.CREATED, StateName.PREPARED], type="int", minValue=1, maxValue=4, default=1)
	cpus = cpus_attr.attribute()
	ram_attr = Attr("ram", desc="RAM", unit="MB", states=[StateName.CREATED, StateName.PREPARED], type="int", minValue=64, maxValue=8192, default=256)
	ram = ram_attr.attribute()
	kblang_attr = Attr("kblang", desc="Keyboard language", states=[StateName.CREATED, StateName.PREPARED], type="str", options=kblang_options, default=None, null=True)
	#["pt", "tr", "ja", "es", "no", "is", "fr-ca", "fr", "pt-br", "da", "fr-ch", "sl", "de-ch", "en-gb", "it", "en-us", "fr-be", "hu", "pl", "nl", "mk", "fi", "lt", "sv", "de"]
	kblang = kblang_attr.attribute()
	usbtablet_attr = Attr("usbtablet", desc="USB tablet mouse mode", states=[StateName.CREATED, StateName.PREPARED], type="bool", default=True)
	usbtablet = usbtablet_attr.attribute()
	template_attr = Attr("template", desc="Template", states=[StateName.CREATED, StateName.PREPARED], type="str", null=True)
    template = models.ForeignKey(Template, null=True)


class KVMQM(RexTFVElement,Element):
	vmid_attr = Attr("vmid", type="int")
	vmid = vmid_attr.attribute()
	websocket_port_attr = Attr("websocket_port", type="int")
	websocket_port = websocket_port_attr.attribute()
	websocket_pid_attr = Attr("websocket_pid", type="int")
	websocket_pid = websocket_pid_attr.attribute()
	vncport_attr = Attr("vncport", type="int")
	vncport = vncport_attr.attribute()
	vncpid_attr = Attr("vncpid", type="int")
	vncpid = vncpid_attr.attribute()
	vncpassword_attr = Attr("vncpassword", type="str")
	vncpassword = vncpassword_attr.attribute()
	cpus_attr = Attr("cpus", desc="Number of CPUs", states=[StateName.CREATED, StateName.PREPARED], type="int", minValue=1, maxValue=4, default=1)
	cpus = cpus_attr.attribute()
	ram_attr = Attr("ram", desc="RAM", unit="MB", states=[StateName.CREATED, StateName.PREPARED], type="int", minValue=64, maxValue=8192, default=256)
	ram = ram_attr.attribute()
	kblang_attr = Attr("kblang", desc="Keyboard language", states=[StateName.CREATED, StateName.PREPARED], type="str", options=kblang_options, default=None, null=True)
	#["pt", "tr", "ja", "es", "no", "is", "fr-ca", "fr", "pt-br", "da", "fr-ch", "sl", "de-ch", "en-gb", "it", "en-us", "fr-be", "hu", "pl", "nl", "mk", "fi", "lt", "sv", "de"]
	kblang = kblang_attr.attribute()
	usbtablet_attr = Attr("usbtablet", desc="USB tablet mouse mode", states=[StateName.CREATED, StateName.PREPARED], type="bool", default=True)
	usbtablet = usbtablet_attr.attribute()
	template_attr = Attr("template", desc="Template", states=[StateName.CREATED, StateName.PREPARED], type="str", null=True)
    template = models.ForeignKey(template.Template, null=True)

class OpenVZ(RexTFVElement,Element):
	vmid_attr = Attr("vmid", type="int")
	vmid = vmid_attr.attribute()
	websocket_port_attr = Attr("websocket_port", type="int")
	websocket_port = websocket_port_attr.attribute()
	websocket_pid_attr = Attr("websocket_pid", type="int")
	websocket_pid = websocket_pid_attr.attribute()
	vncport_attr = Attr("vncport", type="int")
	vncport = vncport_attr.attribute()
	vncpid_attr = Attr("vncpid", type="int")
	vncpid = vncpid_attr.attribute()
	vncpassword_attr = Attr("vncpassword", type="str")
	vncpassword = vncpassword_attr.attribute()
	ram_attr = Attr("ram", desc="RAM", unit="MB", type="int", minValue=64, maxValue=4096, default=256)
	ram = ram_attr.attribute()
	cpus_attr = Attr("cpus", desc="Number of CPUs", type="float", minValue=0.1, maxValue=4.0, default=1.0)
	cpus = cpus_attr.attribute()
	diskspace_attr = Attr("diskspace", desc="Disk space", unit="MB", type="int", minValue=512, maxValue=102400, default=10240)
	diskspace = diskspace_attr.attribute()
	rootpassword_attr = Attr("rootpassword", desc="Root password", type="str")
	rootpassword = rootpassword_attr.attribute()
	hostname_attr = Attr("hostname", desc="Hostname", type="str")
	hostname = hostname_attr.attribute()
	gateway4_attr = Attr("gateway4", desc="IPv4 gateway", type="str")
	gateway4 = gateway4_attr.attribute()
	gateway6_attr = Attr("gateway6", desc="IPv6 gateway", type="str")
	gateway6 = gateway6_attr.attribute()
	template_attr = Attr("template", desc="Template", states=[StateName.CREATED, StateName.PREPARED], type="str", null=True)
    template = models.ForeignKey(Template, null=True)

class Repy(elements.Element):
	pid_attr = Attr("pid", type="int")
	pid = pid_attr.attribute()
	websocket_port_attr = Attr("websocket_port", type="int")
	websocket_port = websocket_port_attr.attribute()
	websocket_pid_attr = Attr("websocket_pid", type="int")
	websocket_pid = websocket_pid_attr.attribute()
	vncport_attr = Attr("vncport", type="int")
	vncport = vncport_attr.attribute()
	vncpid_attr = Attr("vncpid", type="int")
	vncpid = vncpid_attr.attribute()
	vncpassword_attr = Attr("vncpassword", type="str")
	vncpassword = vncpassword_attr.attribute()
	args_attr = Attr("args", desc="Arguments", states=[StateName.PREPARED], default=[])
	args = args_attr.attribute()
	cpus_attr = Attr("cpus", desc="Number of CPUs", states=[StateName.PREPARED], type="float", minValue=0.01, maxValue=4.0, default=0.25)
	cpus = cpus_attr.attribute()
	ram_attr = Attr("ram", desc="RAM", unit="MB", states=[StateName.PREPARED], type="int", minValue=10, maxValue=4096, default=25)
	ram = ram_attr.attribute()
	bandwidth_attr = Attr("bandwidth", desc="Bandwidth", unit="bytes/s", states=[StateName.PREPARED], type="int", minValue=1024, maxValue=10000000000, default=1000000)
	bandwidth = bandwidth_attr.attribute()
	#TODO: use template ref instead of attr
	template_attr = Attr("template", desc="Template", states=[StateName.PREPARED], type="str", null=True)
    template = models.ForeignKey(Template, null=True)

def migrate():
    pass