function validate() {
  var pw1 = document.getElementById("inputPassword").value;
  var pw2 = document.getElementById("inputPassword2").value;
  if(pw1 === pw2) {
    if(pw1.length<6 || pw1.length>16){
      document.getElementById("tishi").innerHTML="<font color='red'>密码长度过长或过短!</font>";
      return false;
    }
    else{
      document.getElementById("tishi").innerHTML="<font color='green'></font>";
      return true;
    }
  }
  else {
     document.getElementById("tishi").innerHTML="<font color='red'>两次密码不相同!</font>";
     return false;
  }
}