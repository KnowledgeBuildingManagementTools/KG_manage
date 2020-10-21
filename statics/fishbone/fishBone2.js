(function(window,$,html2canvas){
      var fishBone = {};
      fishBone.gapStep = 250; // 两块的间隙
      fishBone.style = '#038dc5';// 颜色设定
      fishBone.option = {};
      fishBone.dowload = false; //是否提供下载
      fishBone.axisTpl = `<div class="fish-bone-axis"></div>`;
      fishBone.blockTpl = `
      <div class="fish-bone-block">

        <div class="fish-bone-line upper-line"></div>
        <div class="fish-bone-line lower-line"></div>
        <div class="fish-bone-node active-node"></div>
        <div class="fish-bone-content active-content label-content">
          
        </div>
        <div class="fish-bone-content date-conent active-content">
          
        </div>
      </div>
      `;
      /**line left 21 
       * node left 20
       * label-content left 9
       * date-content left 14
       * 
       * left should be increased by gapStep 
       * 
       * upperline bottom 50
       * lowerline top 50
       * node top 49.5
       * label-content bottom 54
       * date-content 54
       * 
      */
      // 各元素的位置
      var lineLeft = 209,nodeLeft = 200,labelContentLeft = 92,
      dateContentLeft = 140,upperLineBottom = 200,lowerLineTop = 200,
      nodeTop = 195,labelContentBottom = 226,dateContentTop = 226;
      //初始化插件
      fishBone.init = function(container,option){
        this.style = option.color?option.color:this.style;
        this.dowload = option.dowload?option.dowload:this.dowload;
        var data = option.data;
        var len = data.length;
        var tpl = '';
        tpl+=this.axisTpl;
        for(var i=0;i<len;i++){
          tpl+='<div class="fish-bone-block">';
          tpl+='<div class="fish-bone-line upper-line" style="left:'+(lineLeft+this.gapStep*i)+'px;bottom:'+upperLineBottom+'px;"></div>';
          tpl+='<div class="fish-bone-line lower-line" style="left:'+(lineLeft+this.gapStep*i)+'px;top:'+lowerLineTop+'px;"></div>';
          tpl+='<div class="fish-bone-node" style="top:'+nodeTop+'px;left:'+(nodeLeft+this.gapStep*i)+'px;"></div>'
           
          if(i%2==0){
            var pos1 = 'top';
            var pos2 = 'bottom';
            
          }else{
            var pos1 = 'bottom';
            var pos2 = 'top';
          }
          tpl+='<div class="fish-bone-content label-content" style="left:'+(labelContentLeft+this.gapStep*i)+'px;'+pos1+':'+labelContentBottom+'px;">';
          tpl+=data[i].label;
          tpl+='</div>'
          tpl+='<div class="fish-bone-content date-conent" style="left:'+(dateContentLeft+this.gapStep*i)+'px;'+pos2+':'+dateContentTop+'px;">';
          tpl+=data[i].date;
          tpl+='</div>';
          tpl+='</div>';
      
        }
        $(container).html(tpl);
        // 增加轴的长度

        $(".fish-bone-axis").css({"width":(250*len+"px")});
        //设置节点的边框颜色
        var color = this.style;
        $(".fish-bone-node").css({"border-color":color});
        //插入下载按钮
        this.attachClickEvent(container);
      }
      // 绑定点击事件
      fishBone.attachClickEvent = function(container){
        var color = this.style;
        $(".fish-bone-block").on("click",function(){
          $(".fish-bone-content").css({"background-color":"#f5f5f5"});
          $(".fish-bone-node").removeClass("active-node");
          $(this).find(".fish-bone-content").css({"background-color":color});
          $(this).find(".fish-bone-node").addClass("active-node");
          
        });
        $(container+" .fish-bone-download").on("click",function(){
          $(container+" .fish-bone-content").removeClass("active-content").css({"background-color":"#f5f5f5"});
          $(container+" .fish-bone-node").removeClass("active-node");
          html2pic(container);
        });

      }
      // 转图片
      function html2pic(container){
        var el = $(container).get(0);
        var copy = $(container).clone();
        if(html2canvas){
          $width = $(".fish-bone-axis").width()
          // $(container).width($width);
          copy.width($width);
          // $height = $(container).parent().height()
          // $(container).height($height)
          $('body').append(copy);
          el = copy.get(0)
          html2canvas(el, {
            onrendered: function(canvas) {
                
                var url = canvas.toDataURL();
                
                var triggerDownload = $("<a>").attr("href", url).attr("download", "下载.png").appendTo("body");
                triggerDownload[0].click();
                triggerDownload.remove();
                copy.remove();
            }
          });
        }
      }
      window.fishBone = fishBone;
    })(window,jQuery,html2canvas);