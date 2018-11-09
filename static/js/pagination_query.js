$(function(){
    var pagination = $(".pagination");
    var query = "&" + pagination.parent().attr("query");
    pagination.find("a").each(function(e){
        var $this = $(this);
        var href = $this.attr("href");
        if (href)
            $this.attr("href", href + query);
    });
});

