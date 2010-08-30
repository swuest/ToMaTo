package buildui.connectors;

import buildui.paint.MagicTextField;
import buildui.paint.PropertiesArea;
import buildui.paint.NetElement;

/*
 * Copyright (c) 2002-2006 University of Utah and the Flux Group.
 * All rights reserved.
 * This file is part of the Emulab network testbed software.
 * 
 * Emulab is free software, also known as "open source;" you can
 * redistribute it and/or modify it under the terms of the GNU Affero
 * General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 * 
 * Emulab is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
 * more details, which can be found in the file AGPL-COPYING at the root of
 * the source tree.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
public class EmulatedRouterConnectionPropertiesArea extends EmulatedConnectionPropertiesArea {

  public boolean iCare (NetElement t) {
    return t instanceof EmulatedConnection;
  }

  public String getName () {
    return "Link properties";
  }

  public EmulatedRouterConnectionPropertiesArea () {
    super();
    addTextProperty("gateway_ip", "gateway", MagicTextField.ip4_pattern, null);
    addTextProperty("gateway_netmask", "netmask", MagicTextField.ip4_pattern, null);
  }
};
