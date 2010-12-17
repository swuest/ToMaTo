/********************************************************************************
 * Browser quirks:
 * - IE8 does not like a komma after the last function in a class
 * - IE8 does not like colors defined as words, so only traditional colors
 ********************************************************************************/ 

var NetElement = Class.extend({
  init: function(editor){
    this.editor = editor;
    this.selected = false;
    this.editor.addElement(this);
  },
  paint: function(){
  },
  paintUpdate: function(){
    if (this.selected) {
      rect = this.getRect();
      rect = {x: rect.x-5, y: rect.y-5, width: rect.width+10, height: rect.height+10};
      if (!this.selectionFrame) this.selectionFrame = this.editor.g.rect(rect.x, rect.y, rect.width, rect.height).attr({stroke:this.editor.glabColor, "stroke-width": 2});
      this.selectionFrame.attr(rect);
    } else {
      if (this.selectionFrame) this.selectionFrame.remove();
      this.selectionFrame = false;
    }
  },
  getX: function() {
    return this.getPos().x;
  },
  getY: function() {
    return this.getPos().y;
  },
  getWidth: function() {
    return this.getSize().x;
  },
  getHeight: function() {
    return this.getSize().y;
  },
  getRect: function() {
    return {x: this.getX()-this.getWidth()/2, y: this.getY()-this.getHeight()/2, width: this.getWidth(), height: this.getHeight()};
  },
  setSelected: function(isSelected) {
    this.selected = isSelected;
    this.paintUpdate();
  },
  isSelected: function() {
    return this.selected;
  },
  onClick: function(event) {
    if (event.shiftKey) this.setSelected(!this.isSelected());
    else {
      oldSelected = this.isSelected();
      sel = this.editor.selectedElements();
      for (i in sel) sel[i].setSelected(false);
      this.setSelected(!oldSelected | sel.length>1);
    }
  }
});

var IconElement = NetElement.extend({
  init: function(editor, name, iconsrc, iconsize, pos) {
    this._super(editor);
    this.name = name;
    this.iconsrc = iconsrc;
    this.iconsize = iconsize;
    this.pos = pos;
    this.paletteItem = false;
  },
  _dragMove: function (dx, dy) {
    p = this.parent;
    if (p.paletteItem) p.shadow.attr({x: p.opos.x + dx-p.iconsize.x/2, y: p.opos.y + dy-p.iconsize.y/2});
    else p.move({x: p.opos.x + dx, y: p.opos.y + dy});
  }, 
  _dragStart: function () {
    p = this.parent;
    p.opos = p.pos;
    if (p.paletteItem) p.shadow = p.icon.clone().attr({opacity:0.5});
  },
  _dragStop: function () {
    p = this.parent;
    if (p.paletteItem) {
      pos = {x: p.shadow.attr("x")+p.iconsize.x/2, y: p.shadow.attr("y")+p.iconsize.y/2};
      element = p.createAnother(pos);
      element.move(pos);
      p.shadow.remove();
    }
    if (p.pos != p.opos) p.lastMoved = new Date();
  },
  _click: function(event){
    p = this.parent;
    if (p.lastMoved && p.lastMoved.getTime() + 1 > new Date().getTime()) return;
    p.onClick(event);
  },
  paint: function(){
    this._super();
    if (this.text) this.text.remove();
    this.text = this.editor.g.text(this.pos.x, this.pos.y+this.iconsize.y/2+5, this.name).attr({"font-size":12});
    this.text.parent = this;
    this.text.drag(this._dragMove, this._dragStart, this._dragStop);
    if (this.icon) this.icon.remove();
    this.icon = this.editor.g.image(this.iconsrc, this.pos.x-this.iconsize.x/2, this.pos.y-this.iconsize.y/2, this.iconsize.x, this.iconsize.y);
    this.icon.parent = this;
    this.icon.drag(this._dragMove, this._dragStart, this._dragStop);
    this.icon.click(this._click);
  },
  paintUpdate: function() {
    this.icon.attr({x: this.pos.x-this.iconsize.x/2, y: this.pos.y-this.iconsize.y/2});
    this.text.attr({x: this.pos.x, y: this.pos.y+this.iconsize.y/2+5});
    this._super(); //must be at end, so rect has already been updated
  },
  move: function(pos) {
    if (pos.x + this.iconsize.x/2 > this.editor.g.width) pos.x = this.editor.g.width - this.iconsize.x/2;
    if (pos.y + this.iconsize.y/2 + 10 > this.editor.g.height) pos.y = this.editor.g.height - this.iconsize.y/2 - 10;
    if (pos.x - this.iconsize.x/2 < this.editor.paletteWidth) pos.x = this.editor.paletteWidth + this.iconsize.x/2;
    if (pos.y - this.iconsize.y/2 < 0) pos.y = this.iconsize.y/2;
    this.pos = pos;
    this.paintUpdate();
  },
  getPos: function() {
    return this.pos;
  },
  getSize: function() {
    return {x: Math.max(this.text.getBBox().width,this.iconsize.x), y: this.iconsize.y + this.text.getBBox().height};
  },
  getRect: function() {
    return compoundBBox([this.text, this.icon]);
  },
  createAnother: function(pos) {
  }
});

var Connection = NetElement.extend({
  init: function(editor, con, dev) {
    this._super(editor);
    this.con = con;
    this.dev = dev;
    this.paint();
  },
  getPos: function(){
    return {x: (this.con.getX()+this.dev.getX())/2, y: (this.con.getY()+this.dev.getY())/2};
  },
  getSize: function() {
    return {x: 16, y: 16};
  },
  getPath: function(){
    return "M"+this.con.getX()+" "+this.con.getY()+"L"+this.dev.getX()+" "+this.dev.getY();
  },
  paintUpdate: function(){
    this._super();
    this.path.attr({path: this.getPath()});
    this.handle.attr({x: this.getX()-8, y: this.getY()-8});
  },
  paint: function(){
    this._super();
    if (this.path) this.path.remove();
    this.path = this.editor.g.path(this.getPath());
    this.path.toBack();
    if (this.handle) this.handle.remove();
    this.handle = this.editor.g.rect(this.getX()-8, this.getY()-8, 16, 16).attr({fill: "#A0A0A0"});
    this.handle.parent = this;
    this.handle.click(this._click);
  },
  _click: function(event){
    p = this.parent;
    if (p.lastMoved && p.lastMoved.getTime() + 1 > new Date().getTime()) return;
    p.onClick(event);
  }
});

var EmulatedConnection = Connection.extend({
  init: function(editor, dev, con){
    this._super(editor, dev, con);
    this.handle.attr({fill: this.editor.glabColor})
  }
});

var Interface = NetElement.extend({
  init: function(editor, dev, con){
    this._super(editor);
    this.dev = dev;
    this.con = con;
    this.paint();
  },
  getPos: function() {
    xd = this.con.getX() - this.dev.getX();
    yd = this.con.getY() - this.dev.getY();
    magSquared = (xd * xd + yd * yd);
    mag = 14.0 / Math.sqrt(magSquared);
    return {x: this.dev.getX() + (xd * mag), y: this.dev.getY() + (yd * mag)};
  },
  getSize: function() {
    return {x: 16, y: 16};
  },
  paint: function(){
    if (this.circle) this.circle.remove();
    this.circle = this.editor.g.circle(this.getX(), this.getY(), 8).attr({fill: "#CDCDB3"});
    this.circle.parent = this;
    this.circle.click(this._click);
  },
  paintUpdate: function(){
    this._super();
    this.circle.attr({cx: this.getX(), cy: this.getY()});
  },
  showAttributes: function() {
    alert("Interface of " + this.dev.name + " clicked");
    //this.editor.disable();
  },
  _click: function(event) {
    p = this.parent;
    p.onClick(event);
  }
});

var ConfiguredInterface = Interface.extend({
  init: function(editor, dev, con){
    this._super(editor, dev, con);
  }
});

var Connector = IconElement.extend({
  init: function(editor, name, iconsrc, iconsize, pos) {
    this._super(editor, name, iconsrc, iconsize, pos);
    this.connections = [];
    this.paint();
    this.isConnector = true;
  },
  move: function(pos) {
    this._super(pos);
    for (var i in this.connections) {
      this.connections[i].paintUpdate();
      this.connections[i].dev.paintUpdateInterfaces();
    }    
  },
  onClick: function(event) {
    if (event.ctrlKey) {
      selectedElements = this.editor.selectedElements();
      for (i in selectedElements) {
	el = selectedElements[i];
	if (el.isDevice && !this.isConnectedWith(el)) this.editor.connect(this, el);
      }
    } else this._super(event);
  },
  isConnectedWith: function(dev) {
    for (i in this.connections) if (this.connections[i].dev == dev) return true;
    return false;
  },
  createConnection: function(dev) {
    con = new Connection(this.editor, this, dev);
    this.connections.push(con);
    return con;
  }
});

var SpecialConnector = Connector.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/special.png", {x: 32, y: 32}, pos);
  },
  createAnother: function(pos) {
    return new SpecialConnector(this.editor, "special", pos);
  }
});

var HubConnector = Connector.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/hub.png", {x: 32, y: 16}, pos);
  },
  createAnother: function(pos) {
    return new HubConnector(this.editor, "hub", pos);
  },
  createConnection: function(dev) {
    con = new EmulatedConnection(this.editor, this, dev);
    this.connections.push(con);
    return con;
  }
});

var SwitchConnector = Connector.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/switch.png", {x: 32, y: 16}, pos);
  },
  createAnother: function(pos) {
    return new SwitchConnector(this.editor, "switch", pos);
  },
  createConnection: function(dev) {
    con = new EmulatedConnection(this.editor, this, dev);
    this.connections.push(con);
    return con;
  }
});

var RouterConnector = Connector.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/router.png", {x: 32, y: 16}, pos);
  },
  createAnother: function(pos) {
    return new RouterConnector(this.editor, "router", pos);
  },
  createConnection: function(dev) {
    con = new EmulatedConnection(this.editor, this, dev);
    this.connections.push(con);
    return con;
  }
});

var Device = IconElement.extend({
  init: function(editor, name, iconsrc, iconsize, pos) {
    this._super(editor, name, iconsrc, iconsize, pos);
    this.interfaces = [];
    this.paint();
    this.isDevice = true;
  },
  move: function(pos) {
    this._super(pos);
    for (var i in this.interfaces) this.interfaces[i].con.paintUpdate();
    this.paintUpdateInterfaces();   
  },
  paint: function() {
    this._super();
    for (var i in this.interfaces) this.interfaces[i].paint();    
  },
  paintUpdateInterfaces: function() {
    for (var i in this.interfaces) this.interfaces[i].paintUpdate();
  },
  onClick: function(event) {
    if (event.ctrlKey) {
      selectedElements = this.editor.selectedElements();
      for (i in selectedElements) {
	el = selectedElements[i];
	if (el.isConnector && !this.isConnectedWith(el)) this.editor.connect(el, this);
      }
    } else this._super(event);
  },
  isConnectedWith: function(con) {
    for (i in this.interfaces) if (this.interfaces[i].con.con == con) return true;
    return false;
  },
  createInterface: function(con) {
    iface = new Interface(this.editor, this, con);
    this.interfaces.push(iface);
    return iface;
  }
});

var OpenVZDevice = Device.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/computer.png", {x: 32, y: 32}, pos);
  },
  createAnother: function(pos) {
    return new OpenVZDevice(this.editor, "openvz", pos);
  },
  createInterface: function(con) {
    iface = new ConfiguredInterface(this.editor, this, con);
    this.interfaces.push(iface);
    return iface;
  }
});

var KVMDevice = Device.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/pc_green.png", {x: 32, y: 32}, pos);
  },
  createAnother: function(pos) {
    return new KVMDevice(this.editor, "kvm", pos);
  }
});

var Editor = Class.extend({
  init: function(size) {
    this.g = Raphael("editor", size.x, size.y);
    this.size = size;
    this.paletteWidth = 60;
    this.glabColor = "#911A20";
    this.elements = [];
    this.paintPalette();
  },
  paintPalette: function() {
    this.g.path("M"+this.paletteWidth+" 0L"+this.paletteWidth+" "+this.g.height).attr({"stroke-width": 2, stroke: this.glabColor});
    this.openVZPrototype = new OpenVZDevice(this, "OpenVZ", {x: this.paletteWidth/2, y: 50});
    this.openVZPrototype.paletteItem = true;
    this.kvmPrototype = new KVMDevice(this, "KVM", {x: this.paletteWidth/2, y: 100});
    this.kvmPrototype.paletteItem = true;
    this.specialPrototype = new SpecialConnector(this, "Special", {x: this.paletteWidth/2, y: 200});
    this.specialPrototype.paletteItem = true;
    this.hubPrototype = new HubConnector(this, "Hub", {x: this.paletteWidth/2, y: 250});
    this.hubPrototype.paletteItem = true;
    this.switchPrototype = new SwitchConnector(this, "Switch", {x: this.paletteWidth/2, y: 290});
    this.switchPrototype.paletteItem = true;
    this.routerPrototype = new RouterConnector(this, "Router", {x: this.paletteWidth/2, y: 330});
    this.routerPrototype.paletteItem = true;
  },
  connect: function(connector, device) {
    con = connector.createConnection(device);
    iface = device.createInterface(con);
  },
  disable: function() {
    this.disableRect = this.g.rect(0, 0, this.size.x,this.size.y).attr({fill:"#FFFFFF", opacity:.8});
  },
  enable: function() {
    if (this.disableRect) this.disableRect.remove();
  },
  selectedElements: function() {
    sel = [];
    for (i in this.elements) if (this.elements[i].isSelected()) sel.push(this.elements[i]);
    return sel;
  },
  addElement: function(el) {
    this.elements.push(el);
  }
});