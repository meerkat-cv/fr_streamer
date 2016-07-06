var name=document.getElementById( "name_of_user" );
var age=document.getElementById( "age_of_user" );
var course=document.getElementById( "course_of_user" );

$.ajax({
  type: 'post',
  url: 'insertdata.php',
  data: {
    user_name:name,
    user_age:age,
    user_course:course
  },
  success: function (response) {
    $('#success__para').html("You data will be saved");
  }
});