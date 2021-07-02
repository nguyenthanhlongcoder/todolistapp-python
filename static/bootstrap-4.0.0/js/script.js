$(document).ready(function(){
    $("#status").on("change", "input:checkbox", function(){
        $("#submit").submit();
    });
});

jQuery("input[type='checkbox']").change(function() {
jQuery("#form").submit();
});