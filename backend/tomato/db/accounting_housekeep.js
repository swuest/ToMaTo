function() {
  var now = options.now;
  var types = options.types;
  var keep_records = options.keep_records;
  var max_age = options.max_age;

  var combineRecords = function(records) {
    var measurements = 0;
    var usage = {m: 0, d: 0, t: 0, c: 0};
    for (var i=0; i < records.length; i++) {
      var r = records[i];
      measurements += r.m;
      usage.m += r.u.m * r.m;
      usage.d += r.u.d * r.m;
      usage.t += r.u.t;
      usage.c += r.u.c;
    }
    if (measurements > 0) {
      usage.d /= measurements;
      usage.m /= measurements;
    }
    return [usage, measurements];
  };

  var prevPoint = function(point, type) {
    var date = new Date(point*1000);
    switch (type) {
      case "5minutes":
        date.setUTCMinutes(date.getUTCMinutes()-5);
        break;
      case "hour":
        date.setUTCHours(date.getUTCHours()-1);
        break;
      case "day":
        date.setUTCDate(date.getUTCDate()-1);
        break;
      case "month":
        date.setUTCMonth(date.getUTCMonth()-1);
        break;
      case "year":
        date.setUTCFullYear(date.getUTCFullYear()-1);
        break;
    }
    return date.getTime()/1000;
  };

  var nextPoint = function(point, type) {
    var date = new Date(point*1000);
    switch (type) {
      case "5minutes":
        date.setUTCMinutes(date.getUTCMinutes()+5);
        break;
      case "hour":
        date.setUTCHours(date.getUTCHours()+1);
        break;
      case "day":
        date.setUTCDate(date.getUTCDate()+1);
        break;
      case "month":
        date.setUTCMonth(date.getUTCMonth()+1);
        break;
      case "year":
        date.setUTCFullYear(date.getUTCFullYear()+1);
        break;
    }
    return date.getTime()/1000;
  };

  var lastPoint = function(type) {
    var date = new Date(now*1000);
    date.setUTCMilliseconds(0);
    date.setUTCSeconds(0);
    switch (type) {
      case "5minutes":
        date.setUTCMinutes(Math.floor(date.getUTCMinutes()/5)*5);
        break;
      case "year":
        date.setUTCMonth(1);
      case "month":
        date.setUTCDate(1);
      case "day":
        date.setUTCHours(0);
      case "hour":
        date.setUTCMinutes(0);
    }
    return date.getTime()/1000;
  };

  var removeOld = function(obj) {
    var changed = false;
    for (var type in keep_records) {
      var count = keep_records[type];
      if (!obj[type]) continue;
      if (obj[type].length > count) {
        obj[type].splice(0, obj[type].length-count);
        changed = true;
      }
      for (var i=0; i<obj[type].length; i++) {
        if (obj[type][i].e > now + max_age[type]) {
          obj[type].splice(i, 1);
          i-=1;
          changed = true;
        }
      }
    }
    return changed;
  };

  var combine = function(obj) {
    var changed = false;
    var lastList = obj[types[0]];
    if (! lastList) lastList=[];
    for (var i = 1; i<types.length; i++) {
      var type = types[i];
      var list = obj[type];
      if (! list) list=[];
      var begin = list.length > 0 ? list[list.length-1].e : prevPoint(lastPoint(type), type);
      var end = nextPoint(begin, type);
      if (end > now) continue;
      var s = 0;
      for (; s < lastList.length && lastList[s].b < begin; s++);
      while (end <= now) {
        var e = s;
        for (; e < lastList.length && lastList[e].e <= end; e++);
        if (e == lastList.length) break;
        var records = lastList.slice(s, e);
        var t = combineRecords(records);
        var usage = t[0];
        var measurements = t[1];
        list.push({b: begin, e: end, m: measurements, u: usage});
        changed = true;
        begin = end;
        end = nextPoint(end, type);
      }
      obj[type] = list;
    }
    return changed;
  };

  var count = 0;
  db.usage_statistics.find().forEach(function(obj) {
    if (combine(obj) | removeOld(obj)) {
      db.usage_statistics.save(obj);
      count +=1;
    }
  });
  return count;
}
