$(function(){
	/**
	 * 提交修改表单控制
	 */
	//$("#manager_modify_form").submit(function(){
	//	var form = this;
	//	var data = {};
	//	for (var i = 0; i < this.elements.length; i++) {
	//		data[this.elements[i].name] = this.elements[i].value;
	//	}
	//	$.post(this.action, data, function(data){
	//		if (data.errno == 0) {
	//			// 保存成功
	//			$('#modal_success').modal('show');
	//		}
	//	});
	//	return false;
	//});

	/**
	 * 返回上一页
	 */
	$('#modal_success .btn-goback').click(function(){
		history.go(-1);
		return false;
	});
});
