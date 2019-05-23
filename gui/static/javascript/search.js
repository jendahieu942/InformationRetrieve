$("#simple-search-btn").on("click", function () {
    $(".loading-div").css("color", "gray")
    var query_str = $("#simple-search-input").val()
    console.log(query_str);
    if (query_str == null || query_str == "") {
        alert("Query should be not empty");
    } else {
        setTimeout(function () {
            window.location.replace("/search?query=" + query_str);
        }, 500);
    }
});

// $("#simple-search-input").on

$("#simple-search-input").on("keyup", function (e) {
    if (e.keyCode == 13) {
        $("#simple-search-btn").click();
    }
});