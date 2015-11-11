$(window).load(function() {
    var width = $('#clickBlock').width();
    $('#clickBlock').css({'height':width+'px'});

    $("#clickBlock").click(function() {
	// make an ajax call to server to update the clicked count
	$.ajax({
	    url: "/click",
	    success: function(data) {
		$('#thisHourCount').text("clicked " + data.nclick + " times this hour");
	    }
	})
    });


});
