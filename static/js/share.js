document.onreadystatechange = function() {
	if (document.readyState=="complete" || document.readyState=='interactive') {
		initCarousel(carousel);
		document.onreadystatechange = null;
	}

	function initCarousel(carousel) {
		var timer; // 切换计时器
		var SWITCH_TIME = 1000;  // 切换用时
		var SWITCH_TOTAL = 6000; // 停留时间
		var index = 0;

		// 修正百叶窗元素宽度
		var itemWidth;
		var btnbar = carousel.querySelector('.btnbar');
		var container = carousel.querySelector('ul');
		var elems = container.querySelectorAll('li'); // 不包括副本

		window.onresize = function(){
			itemWidth = carousel.offsetWidth;
			container.style.width = itemWidth * (elems.length + 1) + 'px';
			for (var i = 0; i < elems.length; i++) {
				elems[i].style.width = itemWidth + 'px';
			}
		}
		window.onresize();

		// 只有一张图片就不切换
		if (elems.length == 1)
			return;

		for (var i = 0; i < elems.length; i++) {
			// 创建按钮
			var btn = document.createElement('span');
			btn.index = i;
			btn.onclick = onBtnClick;
			btn.onmouseenter = onBtnClick;
			btnbar.appendChild(btn);
		}

		/* 添加副本 */
		container.appendChild(elems[0].cloneNode(true));

		// 按键切换百叶窗
		document.body.onkeydown = function(e) {
			e = e ? e : (window.event ? window.event : "");
            var key = e.keyCode ? e.keyCode : e.which;

			if (key == 37) {
				prev();
			} else if (key == 39) {
				next();
			}
		}

		// prev, next按钮
		// carousel.querySelector('.btn_prev').onclick = prev;
		// carousel.querySelector('.btn_next').onclick = next;

		// 触摸事件
		carousel.addEventListener('touchstart', function(e) {
			this.touchStartX = e.changedTouches[0].clientX;
		}, false);
		carousel.addEventListener('touchend', function(e) {
			offset = e.changedTouches[0].clientX - this.touchStartX;
			if (Math.abs(offset) > 50) {
				if (offset > 0)
					prev();
				else
					next();
			}
		}, false);

		/* 前一张 */
		function prev(){
			if(index == 0){
				index = elems.length;
				container.style.marginLeft = -index * itemWidth + 'px';
			}
			switchTo(index - 1);
		}
		/* 后一张 */
		function next(){
			if (index == elems.length) 
				return;
			switchTo(index + 1, function(){
				if(index == elems.length){
					container.style.marginLeft = 0;
					index = 0;
				}
			});
		}
		/* 切换到指定的元素 */
		function switchTo(i, callback){
			if(index == i)
				return;
			index = i;
			autoNext();
			switchButton();
			container.style.marginLeft = (-itemWidth * i) + 'px';
			callback && callback();
		}
		/* 切换按钮样式 */
		function switchButton(){
			cur = btnbar.querySelector(".active");
			if (cur) {
				// cur.classList.remove("active");
				cur.className = "";
			}
			var i = index == elems.length ? 0 : index;
			// btnbar.children[i].classList.add("active");
			btnbar.children[i].className = "active";
		}
		function autoNext(){
			clearInterval(timer);
			timer = setInterval(next, SWITCH_TOTAL);
		}
		function stopAuto(){
			clearInterval(timer);
		}
		function onBtnClick(){
			switchTo(this.index);
		}
		container.onmouseenter = stopAuto;
		container.onmouseleave = autoNext;
		switchButton();
		autoNext();
	}
}
