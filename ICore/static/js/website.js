$('#tm').bind("click",function(){
  if($('.book').hasClass('with-summary')){
    $('.book').removeClass('with-summary');
  }else{
    $('.book').addClass('with-summary');
  }
});

$('#go-top').click(function(event){
  event.preventDefault();
  $('.body-inner').animate({scrollTop: 0},500);
});

var shareButtonFunc = function(v) {
    var SITES = {
        'facebook': 'http://www.facebook.com/sharer/sharer.php?s=100&p[url]='+encodeURIComponent(location.href),
        'twitter': 'http://twitter.com/home?status='+encodeURIComponent(document.title+' '+location.href),
        'weibo': 'http://service.weibo.com/share/share.php?content=utf-8&url='+encodeURIComponent(location.href)+'&title='+encodeURIComponent(document.title),
        'vk': 'http://vkontakte.ru/share.php?url='+encodeURIComponent(location.href)
    };
    for (var key in SITES) {
        if (key == v) {
            window.open(SITES[key]);
        }
    }
};
//js-toolbar-action
$(".js-toolbar-action").click(function() { 
  shareButtonFunc($(this).attr("id"));
});
