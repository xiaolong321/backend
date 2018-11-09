$(function(){
    $("a").each(function(){
        if(!$(this).attr('href')|| $(this).attr('href')=='') $(this).attr('href', 'javascript:void(0)')
    })
    $(".push-user").click(function(){
        var id = $(this).attr('data-id')
        swal({
            title: "确认将该用户设置为后台发布商品用户？",
            //text: "删除不能恢复，请确认后执行",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确认",
            cancelButtonText: "取消",
            closeOnConfirm: true
        }, function() {
           $.ajax({
                url: '',
                type: 'post',
                dataType: 'json',
                data: { 'user_id': id },
                success: function(result) {
                    if (result.errno == 0) {
                        //$("#msg" + id + "").remove();
                        //location.reload()
                        alert("操作成功")
                    }
                },
                error: function() {
                    alert('请稍后再试')
                }
            }) 

        });
    })
    function modal_ajax(msg, data){
        swal({
            title: msg,
            text: "",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定",
            cancelButtonText: "取消",
            closeOnConfirm: false
        }, function() {
           $.ajax({
                url: '',
                type: 'post',
                dataType: 'json',
                data: data,
                success: function(result) {
                    if (result.errno == 0) {
                        //$("#msg" + id + "").remove();
                        location.reload()
                    }
                },
                error: function() {
                    alert('请稍后再试')
                }
            }) 

        });
    }
    $(".btn-finish-order").click(function(){
        // 完成订单按钮操作
        var id = $(this).attr('data-id')
        modal_ajax('确认完成订单?', {'id': id, 'action': 'finish'}) 
    })
    $(".btn-cacel-order").click(function(){
        // 取消订单按钮操作
        var id = $(this).attr('data-id')
        modal_ajax('确认取消订单?', {'id': id, 'action': 'cacel'}) 
    })
    $(".delete").click(function(){
        var id = $(this).attr('data-id')
        swal({
            title: "确认删除？",
            text: "删除不能恢复，请确认后执行",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "删除",
            cancelButtonText: "取消",
            closeOnConfirm: false
        }, function() {
           $.ajax({
                url: '',
                type: 'post',
                dataType: 'json',
                data: {'id': id, 'action': 'delete'},
                success: function(result) {
                    if (result.errno == 0) {
                        //$("#msg" + id + "").remove();
                        location.reload()
                    }
                },
                error: function() {
                    alert('请稍后再试')
                }
            }) 

        });
    })

});
(function($){
    // jquery 拓展,必填项验证
    $.fn.is_required = function(){
        var value = $(this).val()
        var placeholder = $(this).attr('placeholder')
        if(value==''||value==null){
            $(this).nextAll('i').remove()
            $(this).after("<i class='icon-required'>*</i>")
            $(this).focus()
            return false;
        }
        return true;
    }
})(jQuery)

