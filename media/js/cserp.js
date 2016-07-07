function slideShow(){
    $(function(){ 
        $(".banner .bbg").fadeOut(0).eq(0).fadeIn(0);
        //先隐藏所有图片，再将对象移到第一张图片，使之淡入 
        var i = 0;
        //初始化图片的索引值 
        setInterval(function(){
            //setInterval是每隔一段时间循环一个动作 
            if($(".banner .bbg").length > (i+1)){
                //判断是否执行到最后一张图片 
                $(".banner .bbg").eq(i).fadeOut(2000).next("div").fadeIn(2000);
                //索引值为i的图片淡出，它的下一张图片淡入 
                i++;
                //使索引值增加1，下一次执行动作的图片索引值为i+1， 
            } 
            else{
                //如果为最后一张图片，将执行下面的代码 
                $(".banner .bbg").eq(i).fadeOut(2000).siblings("div").eq(0).fadeIn(2000);
                //索引值为i的图片淡出，这里不同于上面，是第一张图片淡入 
                i = 0;
                //将索引值变为0，回到初始状态 
            }
        },5000);
        //5000ms执行一次淡入淡出的动作 
    }) 
}

//因为delegate,on只能绑定无参数函数，有参数函数会马上执行
//此代码为所有的函数定义了一个函数名为bind的公共静态函数
Function.prototype.bind = function(){   
	var __method = this;   
    var arg = arguments;   
    return function(){   
		__method.apply(window, arg);   
    }   
}




//弹窗函数
//size:1:小，2:中,3:大,4:加大
function newIFrame(strTitle,url,size){
    if(size==1){
	    $.layer({
	        type: 2,
	        title: strTitle,
	        shadeClose: true, //开启点击遮罩关闭层
	        area : ['300px' , '335px'],
	        offset : ['', ''],
	        iframe: {src: url},
	        close : function(index){
			layer.close(index);
			}
	    });
    }
    else if(size==2){
	    $.layer({
	        type: 2,
	        title: strTitle,
	        shadeClose: true, //开启点击遮罩关闭层
	        area : ['800px' , '450px'],
	        offset : ['100px', '200px'],
	        iframe: {src: url},
	        close : function(index){
			layer.close(index);
			}
	    });
    }
    else if(size==3){
	    $.layer({
	        type: 2,
	        title: strTitle,
	        shadeClose: true, //开启点击遮罩关闭层
	        area : ['1000px' , '450px'],
	        offset : ['100px', '200px'],
	        iframe: {src: url},
	        close : function(index){
			layer.close(index);
			}
	    });    
    }
}

//跳转页面
function bindButtonJump(table_selector,button_selector,jurl,title,url,size){
	//selector中含有'#'，需要处理成%23，所以引入encodeURIComponent
    url=url+'?jurl='+encodeURIComponent(jurl)
	$(table_selector).delegate(button_selector,'click',newIFrame.bind(title,url,size));
}

//无额外参数
function bindButton(table_selector,button_selector,id_selector,name_selector,title,url,size){
	//selector中含有'#'，需要处理成%23，所以引入encodeURIComponent
    url=url+'?ids='+encodeURIComponent(id_selector)+'&ns='+encodeURIComponent(name_selector)
	$(table_selector).delegate(button_selector,'click',newIFrame.bind(title,url,size));
}

//传递三个值
function bindButtonThree(table_selector,button_selector,id_selector,name_selector,type_selector,title,url,size){
	//selector中含有'#'，需要处理成%23，所以引入encodeURIComponent
    url=url+'?ids='+encodeURIComponent(id_selector)+'&ns='+encodeURIComponent(name_selector)+'&ts='+encodeURIComponent(type_selector)
	$(table_selector).delegate(button_selector,'click',newIFrame.bind(title,url,size));
}

//带查询参数
function bindButtonPara(table_selector,button_selector,id_selector,name_selector,title,url,search_para,size){
	//selector中含有'#'，需要处理成%23，所以引入encodeURIComponent
    url=url+'?ids='+encodeURIComponent(id_selector)+'&ns='+encodeURIComponent(name_selector)+'&para='+search_para
	$(table_selector).delegate(button_selector,'click',newIFrame.bind(title,url,size));
}



//绑定表格删除行按钮，不提交数据库
//新增行有效
function bindRowDelete(table_selector,delete_class_name){
	//表格里，绑定删除按钮，要求删除按钮具有del样式
	$(table_selector).click(function(e) {
		if (e.target.className==delete_class_name){
			//当内容行只剩一行时不能删除
			if($(e.target).parents("tbody").children().size()>=3){
				$(e.target).parents("tr").remove();
			};
		};
	});
}
//绑定表格鼠标移动，行变色
//新增行有效
function bindMouseMove(table_selector){
	//鼠标在表格上移动
	$(table_selector)
	.delegate('tr','mouseover',function (){
		$(this).addClass("over");
	})
	.delegate('tr','mouseout',function (){
		$(this).removeClass("over");
	});
}

//绑定表格奇偶行颜色不同
//新增行无效
function bindRowColor(table_selector){
	$(table_selector+" tr:even").addClass("alt");
}






//字符串格式化
//用法：'{0}b{1}'.format('a','c');
String.prototype.format = function(){
    var args = arguments;
    return this.replace(/\{(\d+)\}/g,               
        function(m,i){
            return args[i];
        });
}
 
//字符串格式化
//用法String.format('{0}b{1}','a','c')
String.format = function(){
    if( arguments.length == 0 )
        return null;
 
    var str = arguments[0];
    for(var i=1;i<arguments.length;i++) {
        var re = new RegExp('\\{' + (i-1) + '\\}','gm');
        str = str.replace(re, arguments[i]);
    }
    return str;
}

/*
 *  通用JS验证类
 *  使用方法：
 *  var formValidate = new formValidate('fv');
 *  formValidate.init({});
 *  注意：
 *  <form action="" method="post" id="fv"> 
 *  id为fv
 *
 *  <input name="" type="text" validate="zip_code" empty="yes" min=10 max=10 /><span></span>
 *  validate="zip_code"     验证是否是邮政编码
 *  empty="yes"             验证是否允许为空
 *  min=10                  最小长度
 *  max=10                  最大长度
 *  <span></span>           显示提示内容
 */ 
var formValidate = function (selector) { 
 
    var _this = this; 
 
    this.options = { 
        not_null:{reg:/^\S+$/, str:'*'},
        //money:金额,整数部分最长10位,小数部分最长2位
        money:{reg:/^(([1-9]\d{0,9})|0)(\.\d{1,2})?$/,str:'*'},
        //quantity:数量，整数部分最长10位，小数部分最长3位
        quantity:{reg : /^(([1-9]\d{0,9})|0)(\.\d{1,3})?$/ , str : '*'},
        //number:大于零，正整数，用于待摊分期
        number:{reg:/^[1-9]\d{0,20}$/, str : '*'}, 
        //text_number:数字组成字符串，第一个可以为0
        text_number:{reg:/^\d+$/,str:'*'}, 
        //账号，密码
        account:{reg:/^[a-zA-Z][a-zA-Z0-9_]+$/, str:'*'}, 
        password:{reg:/^[\@A-Za-z0-9\!\#\$\%\^\&\*\.\~]+$/, str:'*'},
        chinese:{reg:/^[\u4E00-\u9FA5\uf900-\ufa2d]+$/, str:'必须是中文'}, 
        //手机
        mobile:{reg:/^[1][3-8]+\d{9}$/,str:'*'}, 

    }; 
 
    //初始化 绑定表单 选项 
    this.init = function (options) { 
        this.setOptions(options); 
        this.checkForm(); 
    }; 
 
    //设置参数 
    this.setOptions = function (options) { 
        for (var key in options) { 
            if (key in this.options) { 
                this.options[key] = options[key];    
            } 
        } 
    }; 
 
    //检测表单 包括是否为空，最大值 最小值，正则验证 
    this.checkForm = function () { 
        $(selector).submit(function () { 
            var formChind = $(selector+' :text,:password'); 
            var testResult = true; 
            formChind.each(function (i) { 
                var child       = formChind.eq(i); 
                var value       = child.val(); 
                var len         = value.length; 
                var childSpan   = child.next(); 
 
                //属性中是否为空的情况 
                if (child.attr('empty')) {       
                    if (child.attr('empty') == 'yes' && value == '') { 
                        if (childSpan) { 
                            childSpan.html(''); 
                        } 
                        return; 
                    } 
                } 
 
                //属性中min 和 max 最大和最小长度 
                var min = null; 
                var max = null; 
                if (child.attr('min')) min = child.attr('min'); 
                if (child.attr('max')) max = child.attr('max'); 
                if (min && max) { 
                    if ((len < min || len > max) && (min != max)) { 
                    	if (len==0){
	                    	if (childSpan) { 
	                            childSpan.html(''); 
	                            childSpan.html('*'); 
	                            testResult = false; 
	                            return; 
	                        }                     	
                    	}else{
	                    	if (childSpan) { 
	                            childSpan.html(''); 
	                            childSpan.html(min + '-' + max + '字'); 
	                            testResult = false; 
	                            return; 
	                        } 
                    	}

                    } else if ( min == max && len!=min){
                        if (childSpan) { 
                            childSpan.html(''); 
                            childSpan.html('=' + min +'字'); 
                            testResult = false; 
                            return; 
                        }                     
                    }
                } else if (min) { 
                    if (len < min) { 
                        if (childSpan) { 
                            childSpan.html(''); 
                            childSpan.html('>' + min + '字'); 
                            testResult = false; 
                            return; 
                        } 
                    } 
                } else if (max) { 
                    if (len > max) { 
                        if (childSpan) { 
                            childSpan.html(''); 
                            childSpan.html('<' + max + '字'); 
                            testResult = false; 
                            return; 
                        } 
                    } 
                } 
                 
                //正则校验 
                if (child.attr('validate')) { 
                    var type    = child.attr('validate'); 
                    var result  = _this.check(value, type); 
                    if (childSpan) { 
                        childSpan.html(''); 
                        if (result != true) { 
                            childSpan.html('  ' + result); 
                            testResult = false; 
                        } 
                    } 
                } 
 
            }); 
            return testResult; 
        }); 
    }; 
 
    //检测单个正则选项 
    this.check = function (value, type) { 
        if (this.options[type]) { 
            var val = this.options[type]['reg']; 
            if (!val.test(value)) { 
                return this.options[type]['str']; 
            } 
            return true; 
        } else { 
            return '找不到该表单验证正则项'; 
        } 
    }; 
 
} 
