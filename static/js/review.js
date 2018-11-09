$(document).ready(function() {
    // dataElem 当前tr
    // curData  当前Marker信息
    var map, dataElem, curData;
    var template = document.getElementById('template');
    var mymarker; // 我的当前位置标记

    // 气泡弹框
    var infoWindow = new AMap.InfoWindow({offset: new AMap.Pixel(0, -30)});

    $(".btn_select_community").click(function(){
        if (!map) {
            map = new AMap.Map("map_container", {zoom: 15});
            initMap(map);
        }
        dataElem = $(this).parents('tr');
        var mypos = dataElem.attr('lnglat').split(',');
        mypos = new AMap.LngLat(parseFloat(mypos[0]), parseFloat(mypos[1]));
        map.setCenter(mypos);

        // if (geohash != dataElem.attr('geohash')) {
        //     geohash = dataElem.attr('geohash');
        //     // 清除原先的标记
        //     map.clearMap();
        //     addCommunityMarker(window.community[geohash]);
        // }
        // 清除原先的标记
        map.clearMap();
        addCommunityMarker(window.community[dataElem.index()]);

        // 添加我的位置标记
        if (mymarker)
            map.remove(mymarker);

        mymarker = new AMap.Marker({
            map: map,
            icon: 'http://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
            position: mypos,
        });
        mymarker.on('click', function(){
            $content = $('#myposition', template.content || template).clone();
            $content.find('.lnglat').html(dataElem.attr('lnglat'))
            infoWindow.setContent($content.get(0));
            console.log($content);
            infoWindow.close();
            infoWindow.open(map, mypos);
            map.setCenter(mypos);
        });
        $(modal_map).modal('show');
    });

    /**
     * 初始化地图
     */
    function initMap(map){
        var contextMenu = new AMap.ContextMenu(); //创建右键菜单

        contextMenu.addItem("搜索附件小区", function() {
            $("#lnglat").show();
            document.getElementById("lnglat").value = contextMenu.positon;
            var cpoint = contextMenu.positon; //中心点坐标
            placeSearch.searchNearBy('', cpoint, 200, function(status, result) {
                
            });
        }, 0);
        
        contextMenu.addItem("清除搜索结果", function() {
            if(placeSearch){
                $("#lnglat").hide();
                placeSearch.clear();
            }
        }, 1);

        //地图绑定鼠标右击事件——弹出右键菜单
        map.on('rightclick', function(e) {
            contextMenu.open(map, e.lnglat);
            contextMenu.positon = e.lnglat;
        });

        /**
         * 右键菜单绑定的小区搜索
         */
        var placeSearch;
        AMap.service(["AMap.PlaceSearch"], function() {
            placeSearch = new AMap.PlaceSearch({ //构造地点查询类
                pageSize: 5,
                type: '住宅小区',
                pageIndex: 1,
                map: map,
                panel: "map_panel"
            });
        });

        /**
         * 输入框搜索自动完成
         */
        /*AMap.service(["AMap.Autocomplete"], function() {
            var auto = new AMap.Autocomplete({
                input: "tipinput",
                city:  "南宁",
                citylimit: true,
            });

            //注册监听，当选中某条记录时会触发
            AMap.event.addListener(auto, "select", function(e) {
                if (e.poi && e.poi.location) {
                    map.setZoom(15);
                    map.setCenter(e.poi.location);
                }
            });
        });*/
    }

    /**
     * 添加小区标记
     */
    function addCommunityMarker(datas) {
        if (datas.length == 0)
            return;
        
        for (var i = 0; i < datas.length; i++) {
            var marker = new AMap.Marker({
                position: datas[i].lng_lat.split(','),
                map: map,
            });
            marker.index = i;
            marker.on('click', markerClick);
        }

        /**
         * 预添加的小区标记点击
         * 显示信息框出来
         */
        function markerClick(e) {
            curMakerIndex = e.target.index;
            curData = datas[curMakerIndex];
            var pos  = e.target.getPosition();
            var $content = $('#marker-content', template.content || template).clone();
            $content.find('.marker-name').html(curData.name);
            $content.find('.marker-desc').html(curData.desc);
            $content.find('.btn-usethis').click(onCommunityClick);
            infoWindow.setContent($content.get(0));
            infoWindow.close();
            infoWindow.open(map, pos);
            map.setCenter(pos);
        }
    }

    /**
     * 选中小区按钮点击事件
     */
    function onCommunityClick() {
        var data = {
            gid: dataElem.attr('gid'),
            attr: 'community',
            v: curData.name
        }
        // 发送修改请求
        $.get('/manager/api/update/goods', data, function(data){
            if (data.errno == 0) {
                // 修改按钮前的文本
                dataElem.find('.community').html(curData.name);
                $(modal_map).modal('hide');
            }
        }, 'json');
    }
});
