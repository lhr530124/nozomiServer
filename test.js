var createServer = require("http").createServer;
var sys = require("sys");
var url = require("url");
var qs = require("querystring")
var mysql = require("mysql");
var pool = mysql.createPool({
 host:'127.0.0.1',
 user:'root',
 password:'2e4n5k2w2x',
 socketPath:'/var/run/mysqld/mysqld.sock',
 database: 'nozomi',
    insecureAuth:true,
});

if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}



var ser = exports;
var map = {};
ser.get = function(path, handler){
    map[path] = handler;
};
NOT_FOUND = "not found\n";

var beginTime = 0;

function notFound(req, res) {
    res.writeHead(404, {"Content-Type":"text/plain", "Content-Length":NOT_FOUND.length});
    res.end(NOT_FOUND)
}
var server = createServer(function(req, res){
    if(req.method === "GET" || req.method === "HEAD") {
        var handler = map[url.parse(req.url).pathname] || notFound;
        res.simpleText=function(code, body){
            res.writeHead(code, {"Content-Type":"text/plain", "Content-Length":body.length});
            res.end(body);
        };
        res.simpleJSON = function(code, obj){
            var body = new Buffer(JSON.stringify(obj));
            res.writeHead(code, {"Content-Type":"application/json", "Content-Length":body.length});
            try{
                res.end(body);
            }
            catch(err)
            {
                sys.puts("send error");
            }
        };
        handler(req, res);
    }
});
ser.listen=function(port, host){
  server.listen(port, host);
  sys.puts("Server at http://"+(host||"127.0.0.1")+":"+port.toString()+"/");
};

HOST = null;
port = 8005;

var channels = {};//cid channel
function createChannel(cid)
{
    var channel = channels[cid];
    if(channel)
        return channel;

    function deleteMsg(msg) {
        pool.getConnection(function(err, connection) {
            console.log("connection Error", err);
            connection.query(
            "delete from chatMessage where cid = {0} and mid = {1}  and uid = {2}".format(cid, msg[3], msg[0]), 
            function(err, rows) {
                console.log("query error", err);
                connection.release();
            });

        });
    }

    var channel = new function() {
        var messages = [];
        var donates = [];
        var callbacks = [];
        var lastTime = 0;
        //异步的初始化channel 所以要等 channel 初始化结束了 才能返回数据
        function initMessage() {
            pool.getConnection(function(err, connection) {
                console.log("connection Error", err);
                connection.query(
                "select mid, uid, name, type, text  from chatMessage where cid = {0} ".format(cid), 
                function(err, rows, fields) {
                    console.log("initMessage", rows);
                    for(var i in rows) {
                       var msg = rows[i];
                       if(msg.type === "msg" || msg.type === "join" || msg.type === "part" || msg.type == "sys") {
                            var m = [msg.uid, msg.name,  msg.text, msg.mid, msg.type];
                            messages.push(m);
                       } else if(msg.type === "request") {
                            var m = [msg.uid, msg.name, JSON.parse(msg.text), msg.mid, msg.type];
                            messages.push(m);
                       } else {
                            console.log("Error initMessage", msg);
                       }
                    }
                    connection.release();

                    var matching = [];
                    for(var i = 0; i < messages.length; i++){
                        var message = messages[i];
                        matching.push(message);
                    }
                    console.log("matchInfo", matching.length);
                    //初始化结束 调用所有的回调函数返回数据
                    if(matching.length > 0) {
                        while(callbacks.length>0){
                            callbacks.shift().callback(matching);
                        }
                    }

                });

            });
        }



        //多种类型消息 appendMessage
        this.appendMessage = function(uid, name, type, text){
            uid = parseInt(uid, 10)
            switch(type){
            case "msg":
                sys.puts("<"+uid+">"+text);
                break;
            case "join":
                sys.puts(nick+" join");
                break;
            case "part":
                sys.puts(nick+" part");
                break;
            };
            var cur = Math.floor((new Date()).getTime()/1000);
            if(lastTime>=cur){
                lastTime = lastTime+1;
                cur = lastTime;
            }
            else
                lastTime = cur
            var m = [uid, name,  text, (cur - beginTime), type];
            pool.getConnection(function(err, connection) {
                console.log("connection Error", err);
                connection.query(
                "insert into chatMessage (cid, mid, uid, name, type, text) values({0}, {1}, {2}, '{3}', '{4}', '{5}')".format(cid, cur-beginTime, uid, name, type, text), 
                function(err, rows) {
                    console.log("query error", err);
                    connection.release();
                });

            });

            messages.push(m);
            while(callbacks.length>0){
                callbacks.shift().callback([m]);
            }
            while(messages.length > 100) {
                var dm = messages.shift();
                deleteMsg(dm);
            }
        };
        this.appendSys=function(type, info){
            cur = Math.floor((new Date()).getTime()/1000);

            if(lastTime>=cur){
                lastTime = lastTime+1;
                cur = lastTime;
            }
            else
                lastTime = cur;
            m = [0, type, info, cur-beginTime, "sys"];

            pool.getConnection(function(err, connection) {
                console.log("connection Error", err);
                connection.query(
                "insert into chatMessage (cid, mid, uid, name, type, text) values({0}, {1}, {2}, '{3}', '{4}', '{5}')".format(cid, cur-beginTime, 0, type, 'sys', info), 
                function(err, rows) {
                    console.log("query error", err);
                    connection.release();
                });

            });

            messages.push(m);
            while(messages.length>100) {
                var msg = messages.shift();
                deleteMsg(msg);
            }
            while(callbacks.length>0){
                callbacks.shift().callback([m]);
            }
        }
        this.appendRequest=function(uid, name, space, max){
            //删除旧的请求士兵的请求
            for(var i=0; i < messages.length; i++){
                if (messages[i][4]=="request" && messages[i][0]==uid){
                    var m = messages.splice(i, 1);
                    deleteMsg(m[0]);
                    break;
                }
            }
            cur = Math.floor((new Date()).getTime()/1000);
            if(lastTime>=cur){
                lastTime = lastTime+1;
                cur = lastTime;
            }
            else
                lastTime = cur;
            m = [uid, name, [space, max, []], (cur-beginTime), "request"];

            pool.getConnection(function(err, connection) {
                console.log("connection Error", err);
                connection.query(
                "insert into chatMessage (cid, mid, uid, name, type, text) values({0}, {1}, {2}, '{3}', '{4}', '{5}')".format(cid, cur-beginTime, uid, name, 'request', JSON.stringify([space, max, []])), 
                function(err, rows) {
                    console.log("query error", err);
                    connection.release();
                });

            });

            messages.push(m);
            while(callbacks.length>0){
                callbacks.shift().callback([m]);
            }
            while(messages.length>100) {
                var msg = messages.shift();
                deleteMsg(msg);
            }
        };
        this.appendDonate=function(uid, toUid, sid, slevel, space){
            cur = Math.floor((new Date()).getTime()/1000);

            if(lastTime>=cur){
                lastTime = lastTime+1;
                cur = lastTime;
            }
            else
                lastTime = cur;
            //var update=[toUid, sid, slevel, (cur-beginTime), "donate"];
            for(var i=0; i<messages.length; i++){
                //给该用户赠送兵力
                if (messages[i][4]=="request" && messages[i][0]==toUid){
                    property = messages[i][2];
                    if(property[0]+space>property[1]){
                        break;
                    }
                    property[0] += space;

                    //update.push(property[0]);
                    var helps = property[2];
                    helps.push([uid, sid, slevel])
                    var m = messages[i];
                    console.log("doDonate", m);

                    pool.getConnection(function(err, connection) {
                        console.log("connection Error", err);
                        connection.query(
                        "update chatMessage set text = '{0}' where cid = {1} and uid = {2} and type = '{3}' and mid = {4}".format(JSON.stringify(property), cid, toUid, 'request', m[3]), 
                        function(err, rows) {
                            console.log("query error", err);
                            connection.release();
                        });

                    });

                    var dm = [toUid, uid, property, (cur-beginTime), "donate"];
                    donates.push(dm);
                    while(donates[0][3]<=cur-beginTime-60){
                        donates.shift();
                    }
                    while(callbacks.length>0){
                        callbacks.shift().callback([dm]);
                    }
                }
            }
            //while(callbacks.length>0){
            //    callbacks.shift().callback([update]);
            //}
        };
        this.query=function(since, callback){
            var matching = [];
            for(var i = 0; i < messages.length; i++){
                var message = messages[i];
                if(message[3] > since) {
                    matching.push(message);
                }
            }
            for(var i = 0; i < donates.length; i++){
                var donate = donates[i];
                if(donate[3] > since && donate[3]<since+60) {
                    matching.push(donate);
                }
            }

            if(matching.length > 0)//have message to send callback
                callback(matching);
            else
                callbacks.push({timestamp:new Date(), callback: callback});//no message just hold on 
        };
        //从数据库初始化 消息 
        initMessage();
        console.log("msg Length", messages.length);

        setInterval(function(){//remove long callbacks
            var now = new Date();
            while(callbacks.length > 0 && now - callbacks[0].timestamp > 30*1000) {
                callbacks.shift().callback([]);//return empty message
            }
        }, 3000);
    };
    channels[cid] = channel;
    return channel;
}


ser.listen(Number(process.env.port||port), HOST);
//first time receive or send will join
ser.get("/send", function(req, res){
    var uid = qs.parse(url.parse(req.url).query).uid;
    var name = qs.parse(url.parse(req.url).query).name;
    var cid = qs.parse(url.parse(req.url).query).cid;
    var text = qs.parse(url.parse(req.url).query).text;
    sys.puts("send " + uid + " "+ name +" "+cid +" " + text);
    channel = createChannel(cid)
    channel.appendMessage(uid, name, "msg", text);
    res.simpleJSON(200, {result: "send suc"});
});
ser.get("/sys", function(req, res){
    var args = qs.parse(url.parse(req.url).query);
    var type = args.type;
    var info = args.info;
    var cid = args.cid;
    channel = createChannel(cid);
    sys.puts("sys " + cid + " " + type + " " + info)
    channel.appendSys(type, info);
    res.simpleJSON(200, {result: "send suc"});
});
ser.get("/request", function(req, res){
    var args = qs.parse(url.parse(req.url).query);
    var uid = parseInt(args.uid, 10);
    var name = args.name;
    var cid = args.cid;
    var space = parseInt(args.space, 10);
    var max = parseInt(args.max, 10);
    channel = createChannel(cid);
    channel.appendRequest(uid, name, space, max);
    sys.puts("request " + uid + " " + name + " "+cid + " " + space);
    res.simpleJSON(200, {result: "send suc"});
});
ser.get("/donate", function(req, res){
    var args = qs.parse(url.parse(req.url).query);
    var uid = parseInt(args.uid, 10);
    var toUid = parseInt(args.toUid, 10);
    var cid = args.cid;
    var sid = parseInt(args.sid, 10);
    var slevel = parseInt(args.slevel, 10);
    var space = parseInt(args.space, 10);
    channel = createChannel(cid);
    channel.appendDonate(uid, toUid, sid, slevel, space);
    res.simpleJSON(200, {result: "send suc"});
});
ser.get("/recv", function(req, res){
    if(!qs.parse(url.parse(req.url).query).since){
        res.simpleJSON(400, {error:"no since"});
        return;
    }
    var uid = qs.parse(url.parse(req.url).query).uid;
    var cid = qs.parse(url.parse(req.url).query).cid;
    var since = parseInt(qs.parse(url.parse(req.url).query).since, 10);
    sys.puts("recv "+uid+" "+cid);
    channel = createChannel(cid)
    channel.query(since, function(messages){//callback function
        res.simpleJSON(200, {messages: messages});
    });
});
