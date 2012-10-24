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

from tomato import elements
import generic

class OpenVZ(generic.VMElement):
	TYPE = "openvz"
	DIRECT_ATTRS_EXCLUDE = ["ram", "diskspace"]
	CAP_CHILDREN = {
		"openvz_interface": [generic.ST_CREATED, generic.ST_PREPARED],
	}
	PROFILE_ATTRS = ["ram", "diskspace"]
	
	class Meta:
		db_table = "tomato_openvz"
		app_label = 'tomato'

class OpenVZ_Interface(generic.VMInterface):
	TYPE = "openvz_interface"
	CAP_PARENT = [OpenVZ.TYPE]
	
	class Meta:
		db_table = "tomato_openvz_interface"
		app_label = 'tomato'
	
elements.TYPES[OpenVZ.TYPE] = OpenVZ
elements.TYPES[OpenVZ_Interface.TYPE] = OpenVZ_Interface