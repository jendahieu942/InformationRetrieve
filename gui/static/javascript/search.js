$("#simple-search-btn").on("click", function () {
    console.log("Clicked");
    alert("Click search");
});
$("#simple-search-input").on("keyup", function (e) {
    if (e.keyCode == 13) {
        $("#simple-search-btn").click();
    }
});