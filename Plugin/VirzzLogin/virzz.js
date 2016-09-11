var xhr;
var password = "your password";
var domain = "https://www.yourdomain.com";
var tabid;

chrome.browserAction.onClicked.addListener(function queryTab(tab){
    chrome.tabs.create({url:domain}, function(tab){
        tabid = tab.id;
        login();
    });
});

function install(){
  json = {"setup":{"username":"Yourname", "password":password}};
  xhr = new XMLHttpRequest();
  xhr.onreadystatechange = installFun;
  xhr.open("POST", domain+"/install.vir", true);
  xhr.setRequestHeader("Content-Type","application/json"); 
  xhr.send(JSON.stringify(json));
}

function installFun(){
    if(xhr.readyState == 4 && xhr.status == 200){  
        if(xhr.responseText == "1"){
            chrome.tabs.create({url:domain+"/roots/setting.vir"});
            chrome.tabs.remove(tabid);
        }else{    
            login();   
        }           
    }
}

function login() {
    json = {"login":{"username":"Yourname", "password":password}};
    xhr = new XMLHttpRequest();
    xhr.onreadystatechange = loginFun;
    xhr.open("POST", domain+"/roots/login.vir", true);
    xhr.setRequestHeader("Content-Type","application/json"); 
    xhr.send(JSON.stringify(json));
}


function loginFun(){
    if(xhr.readyState == 4 && xhr.status == 200){  
        if(xhr.responseText == "1"){
            chrome.tabs.remove(tabid);
            chrome.tabs.create({url:domain+"/roots/setting.vir"});
        }else if (xhr.responseText == "init"){    
            install();  
        }
    }
}
