{   
    var index = 0;//初始下标
    var indexArr= new Array();
    function add1() {
        index++;
        indexArr.push(index);
        var tbody = document.getElementById('body1');
        //创建节点
        var tr = document.createElement('tr');
        tr.id='tr##'.replace(/##/g,index);
        var td1 = document.createElement('td');
        var td2 = document.createElement('td');
        var td3 = document.createElement('td');
        var input1=document.createElement('input');
        var input2=document.createElement('input');
        var div=document.createElement('div');
        var label=document.createElement('label');
        var button=document.createElement('button');

        input1.type='text';
        input1.setAttribute('class','form-control');
        input1.id='inputName';
        input1.placeholder='字段名称';


        input2.type='file';
        input2.setAttribute('class','custom-file-input');
        input2.id='file##'.replace(/##/g,index);
        input2.onchange=function(){
            var file = document.getElementById(input2.id);
            var fileName = document.getElementById(label.id);
            fileName.innerHTML = file.value;
        };

        div.setAttribute('class','custom-file');
        div.id='image';

        label.setAttribute('class','custom-file-label');
        label.for='exampleInputFile';
        label.id='fileName##'.replace(/##/g,index);
        label.innerHTML='添加图片'

        button.setAttribute('class','btn btn-danger');
        button.type='button';
        button.innerHTML='删除';
        button.setAttribute('onclick','deleteRow2("##")'.replace(/##/g,index));
        

        div.append(input2);
        div.append(label);

        td1.append(input1);
        td2.append(div);
        td3.append(button);
        //添加内容到表格中
        tr.append(td1);
        tr.append(td2);
        tr.append(td3);
        tbody.append(tr);
    }
    
    //删除一行
    function deleteRow(inde){
        $("#tr" + inde).remove();
        var a = indexArr.indexOf(parseInt(inde));
    
        if (a > -1) {
            indexArr.splice(a, 1);
            console.log("当前下标数组",indexArr);
        }
    }
}

{   
    var index = 0;//初始下标
    var indexArr= new Array();
    function add2() {
        index++;
        indexArr.push(index);
        var tbody = document.getElementById('body2');
        //创建节点
        var tr = document.createElement('tr');
        tr.id='tr##'.replace(/##/g,index);
        var td1 = document.createElement('td');
        var td2 = document.createElement('td');
        var td3 = document.createElement('td');
        var input1=document.createElement('input');
        var input2=document.createElement('input');
        var div=document.createElement('div');
        var label=document.createElement('label');
        var button=document.createElement('button');
    
        input1.type='text';
        input1.setAttribute('class','form-control');
        input1.id='inputName';
        input1.placeholder='参数名称';
    
    
        input2.type='file';
        input2.setAttribute('class','custom-file-input');
        input2.id='file##'.replace(/##/g,index);
        input2.onchange=function(){
            var file = document.getElementById(input2.id);
            var fileName = document.getElementById(label.id);
            fileName.innerHTML = file.value;
        };
    
        div.setAttribute('class','custom-file');
        div.id='image';
    
        label.setAttribute('class','custom-file-label');
        label.for='exampleInputFile';
        label.id='fileName##'.replace(/##/g,index);
        label.innerHTML='添加图片'
    
        button.setAttribute('class','btn btn-danger');
        button.type='button';
        button.innerHTML='删除';
        button.setAttribute('onclick','deleteRow2("##")'.replace(/##/g,index));
        
    
        div.append(input2);
        div.append(label);
    
        td1.append(input1);
        td2.append(div);
        td3.append(button);
        //添加内容到表格中
        tr.append(td1);
        tr.append(td2);
        tr.append(td3);
        tbody.append(tr);
    }

    //删除一行
    function deleteRow2(inde){
        $("#tr" + inde).remove();
        var a = indexArr.indexOf(parseInt(inde));
    
        if (a > -1) {
            indexArr.splice(a, 1);
            console.log("当前下标数组",indexArr);
        }
    }
}

function handleFile1(){
    var file = document.getElementById("file-1");
    var fileName = document.getElementById("fileName-1");
    fileName.innerHTML = file.value;
}

function handleFile2(){
    var file = document.getElementById("file-2");
    var fileName = document.getElementById("fileName-2");
    fileName.innerHTML = file.value;
}