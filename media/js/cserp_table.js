/* 
要求具备下列条件
添加，编辑，删除按钮的id分别为btnNew,btnEdit,btnDelete
表格命名为dt
表格第一行的单元格第一个元素为checkbox
其余checkbox位于第一列
删除时post的name是ids，传递的是item项目id字典字符串 i。
var str_json="{\
	urlNew:'/start_setting/1002/new/{{s.id}}',\
	urlEdit:'/start_setting/1002/edit/',\
	urlDelete:'/start_setting/delete',\
	flagDelete:{sid:{{s.id}}}\
}";
flagDelete也是json，可以传递其他参数，本函数自动附加键值为ids的删除id字符串，id间用逗号隔开。
 */


function table(strJson){

	var objJson=eval('('+strJson+')');
	//有些表头是th
	var boolHasTh=$("#dt tr th").length>0 ? true:false;
	var chkTitle=boolHasTh ? $("#dt tr th input[type=checkbox]"):$("#dt tr td input[type=checkbox]").first();
	var chkItems=boolHasTh ? $("#dt tr td input[type=checkbox]").not("[disabled]"):$("#dt tr td input[type=checkbox]").slice(1).not("[disabled]");
	var btnNew=$("#btnNew");
	var btnEdit=$("#btnEdit");
	var btnDelete=$("#btnDelete");
  	
  	
  	//处理全选事件
    chkTitle.on('click',function(){
		if (chkTitle.is(":checked")){
			chkItems.prop("checked",true);//全选
			btnDelete.show();
		}
		else{
			chkItems.prop("checked",false);//全不选 
			btnDelete.hide();
		}
		relate_pro();
	});

	//处理checkbox事件
	chkItems.on('click',function(){
		relate_pro();
	});
	
	//获得checkbox为true的数目
	function get_chk_num(){
		var chkItemsArray=chkItems.toArray();	//全部Item的checkbox数组
		var numCheck=0;
		$.each(chkItemsArray,function(){
			if(this.checked){
				numCheck++;
			}
		});
		return numCheck;
	}
	
	//处理点击联动
	function relate_pro(){
		var chkItemsArray=chkItems.toArray();
		var numCheck=get_chk_num();
		
		if(numCheck==chkItemsArray.length){
			chkTitle.prop("checked",true);
		}else{
			chkTitle.prop("checked",false);
		}
		
		if(numCheck>0){
			btnDelete.show();
		}else{
			btnDelete.hide();
		}
		
		if(numCheck==1){
			btnEdit.show();
		}
		else{
			btnEdit.hide();
		}
	}
	
	//点击行处理checkbox和edit按钮
	$("#dt tr").slice(1).each(function(){  
	    var p = this;
	    //$(this).children().slice(1)表示此行除第一格的单元格  
	    $(this).children().slice(1).click(function(){  
	        $($(p).children()[0]).children().each(function(){  
	            if(this.type=="checkbox" && this.disabled==false){  
	                if(!this.checked){  
	                    this.checked = true;
	                }else{  
	                    this.checked = false;  
	                }  
	            }
	        });  
	    relate_pro();
	    });  
	});
	
	//新增按钮
	btnNew.on('click',function(){
		location.href = objJson.urlNew;
	});
	
	//编辑按钮
	btnEdit.on('click',function(){
		var str = '';
		chkItems.each(function(){
			if ($(this).prop("checked")){ //判断是否选中     
                str=$(this).val();
        	}  
		});
		location.href = objJson.urlEdit+str;
	});
	
	//删除按钮
	//btnDelete.click(function(){
	btnDelete.on('click',function(){
		var str = '';
		chkItems.each(function(){
			if ($(this).prop("checked")){ //判断是否选中    
                //alert($(this).val());  
                //array.push($(this).val()); //将选中的值 添加到 array中  
                str+=$(this).val()+",";  //后面多一个逗号
        	}  
		});
		str=str.substring(0,str.length-1); //去掉逗号
		objJson.flagDelete.ids=str;

		$.post(objJson.urlDelete,objJson.flagDelete,
            function(ret){          
	        	if(ret==1){
					location.reload();
		        }  
		        else{  
		            msg.html("该项已不能删除！");  
		        }  
		    }
		);

	});
}

