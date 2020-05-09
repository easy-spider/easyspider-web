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
        var td4 = document.createElement('td');
        var input1=document.createElement('input');
        var input2=document.createElement('input');
        var input3=document.createElement('input');
        var div=document.createElement('div');
        var label=document.createElement('label');
        var button=document.createElement('button');
        var img_div=document.createElement('div');
        var img=document.createElement('img');
        var input_div=document.createElement('div');

        img_div.setAttribute('class','input-group-text menu');
        img_div.innerHTML='预览图片';

        img.height='400';
        img.id='img##'.replace(/##/g,index);
        img.src='';

        input_div.setAttribute('class','input-group-append');

        input1.type='text';
        input1.setAttribute('class','form-control');
        input1.id='inputName';
        input1.placeholder='字段英文名称';

        input3.type='text';
        input3.setAttribute('class','form-control');
        input3.id='inputName';
        input3.placeholder='字段中文名称';


        input2.type='file';
        input2.setAttribute('class','custom-file-input');
        input2.id='file##'.replace(/##/g,index);
        input2.onchange=function(){
            var file = document.getElementById(input2.id);
            var fileName = document.getElementById(label.id);
            fileName.innerHTML = file.value;
        };
        input2.addEventListener('change', function () {
            var file = this.files[0];
            var reader = new FileReader();
            reader.addEventListener("load", function () {
                img.src = reader.result;
            }, false);
            reader.readAsDataURL(file);
        }, false);

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
        

        img_div.append(img);
        input_div.append(input2);
        input_div.append(img_div);

        div.append(input_div);
        div.append(label);

        td1.append(input1);
        td2.append(input3);
        td3.append(div);
        td4.append(button);
        //添加内容到表格中
        tr.append(td1);
        tr.append(td2);
        tr.append(td3);
        tr.append(td4);
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
        var td4 = document.createElement('td');
        var td5 = document.createElement('td');
        var td6 = document.createElement('td');
        var input1=document.createElement('input');
        var input2=document.createElement('input');
        var input3=document.createElement('input');
        var div=document.createElement('div');
        var label=document.createElement('label');
        var button=document.createElement('button');
        var input_label_div=document.createElement('div');
        var input_type_div=document.createElement('div');
        var input_label_select=document.createElement('select');
        var input_type_select=document.createElement('select');
        var option1=document.createElement('option');
        var option2=document.createElement('option');
        var option3=document.createElement('option');
        var option4=document.createElement('option');
        var img_div=document.createElement('div');
        var img=document.createElement('img');
        var input_div=document.createElement('div');

        img_div.setAttribute('class','input-group-text menu');
        img_div.innerHTML='预览图片';

        img.height='400';
        img.id='img##'.replace(/##/g,index);
        img.src='';

        input_div.setAttribute('class','input-group-append');

    
        input1.type='text';
        input1.setAttribute('class','form-control');
        input1.id='inputName';
        input1.placeholder='参数英文名称';

        input3.type='text';
        input3.setAttribute('class','form-control');
        input3.id='inputName';
        input3.placeholder='参数中文名称';

    
    
        input2.type='file';
        input2.setAttribute('class','custom-file-input');
        input2.id='file##'.replace(/##/g,index);
        input2.onchange=function(){
            var file = document.getElementById(input2.id);
            var fileName = document.getElementById(label.id);
            fileName.innerHTML = file.value;
        };
        input2.addEventListener('change', function () {
            var file = this.files[0];
            var reader = new FileReader();
            reader.addEventListener("load", function () {
                img.src = reader.result;
            }, false);
            reader.readAsDataURL(file);
        }, false);

    
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
        
        input_label_div.setAttribute('class','form-group');
        input_type_div.setAttribute('class','form-group');
        input_label_select.setAttribute('class','custom-select');
        input_type_select.setAttribute('class','custom-select');
        option1.innerHTML='input';
        option2.innerHTML='textarea';
        option3.innerHTML='input';
        option4.innerHTML='number';

        input_label_select.append(option1);
        input_label_select.append(option2);
        input_type_select.append(option3);
        input_type_select.append(option4);
    
        input_label_div.append(input_label_select);
        input_type_div.append(input_type_select);


        img_div.append(img);
        input_div.append(input2);
        input_div.append(img_div);


        div.append(input_div);
        div.append(label);
    
        td1.append(input1);
        td2.append(input3);
        td5.append(input_label_div);
        td6.append(input_type_div);
        td3.append(div);
        td4.append(button);
        //添加内容到表格中
        tr.append(td1);
        tr.append(td2);
        tr.append(td5);
        tr.append(td6);
        tr.append(td3);
        tr.append(td4);
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