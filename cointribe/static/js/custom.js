
function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function eraseCookie(name) {
    document.cookie = name+'=; Max-Age=-99999999;';
}

function initHeaderSigninForm(){
    $("#sign_in").validate({
        onfocusout: false,
        invalidHandler: function(e, validator) {
            var errors = validator.numberOfInvalids();
            if (errors) {
                validator.errorList[0].element.focus();
                $("#signin_error").html(validator.errorList[0].message);
                $("#signin_error").show();
                //setTimeout('$("#signin_error").slideUp()', 10000);
            } else {
                $("#signin_error").hide();
            }
        },
        rules: {
            username : { required: true, email : true,},
            password : "required"
        },
        messages: {               //messages to appear on error
            username : {required : "Provide email address to login.", email : "Enter a valid email address."},
            password : "Provide password to login."
        },
        errorPlacement: function(error, element) {
            // Override error placement to not show error messages beside elements //
        },
        submitHandler:function(form){
            $.ajax({
                data: $(form).serialize(),
                type: $(form).attr('method'),
                url: $(form).attr('action'),
                success: function(response) {
                    if(response.status == 203){
                    $("#signin_error").show();
                    $("#signin_error").html(response.usermsg);
                    }else{
                    setCookie('ppktk',response.token,2)
                    $("#signin_error").show();
                    $("#signin_error").html(response.usermsg);
                    history.pushState("", "", response.redirect);
                      $.ajaxSetup({
            headers: { 'Authorization': "Token "+getCookie('ppktk') }
            });
                   $.ajax({
                        type: "GET",
                        url: response.redirect,
                        success: function(response) {
                            console.log(response)
                            $('body').html(response)

                        },
                        error: function(response) {

                    //Set a mesage to show error
                }

                        });
                }
                },
                error: function(response) {
                    $("#signin_error").show();
                    $("#signin_error").html(response.usermsg);
                    //Set a mesage to show error
                }
            });
        }
    });
}
function callAuthHeader(){
    $.ajaxSetup({
            headers: { 'Authorization': "Token "+getCookie('ppktk') }
            });
}

function logout(){
    eraseCookie("ppktk")
    document.location="/login"
}
// funtion add / update / delete
function inventoryAction(action,id=""){
    if(action == "update"){
        form="#inventory_update_"+id
        action="inventory/"+id+"/"
        type="PUT"
    }
    if(action=="add"){
        form="#inventory_add"
        action="inventory"
        type="POST"
    }
    if(action=="delete"){
        form="#inventory_delete_"+id
        action="inventory/"+id+"/"
        type="DELETE"
    }
    callAuthHeader();
      $.ajax({
                data: $(form).serialize(),
                type: type,
                url: action,
                success: function(response) {
                    console.log(response)
                    alert(response.msg)
                },
                error: function(response) {

                    //Set a mesage to show error
                }
            });
            return false
}
function GetPermission(action){
  data={"action":action,"admin_name":"inventory"}
  callAuthHeader();
  $.ajax({
                data: data,
                type: "POST",
                url: "inventoryAproved",
                success: function(response) {
                    alert(response)
                },
                error: function(response) {
                    alert("There is some error")
                    //Set a mesage to show error
                }
            });

}
function showPermission(){
callAuthHeader();
            $.ajax({
                type: "GET",
                url: "inventoryAproved",
                success: function(response) {
                    $("#list_permission").html(response)
                },
                error: function(response) {
                    alert("There is some error")
                }
            });
}
//funtion to approve permission
function approvePermission(id){
    callAuthHeader();
    $.ajax({
                type: "PUT",
                url: "inventoryAproved/"+id+"/",
                success: function(response) {
                    alert(response)
                    showPermission()
                    $('#ShowPermissions').modal('show');
                },
                error: function(response) {
                    alert("There is some error")
                }
            });

}