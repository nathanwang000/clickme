$(window).load(function() {
    // var h = $('#clickBlock').height();
    // $('#clickBlock').css({'width':h+'%'});
    var w = $('#clickBlock').width();
    $('#clickBlock').css({'height':w+'px'});

    $("#clickBlock").click(function() {
	// make an ajax call to server to update the clicked count
	$.ajax({
	    url: "/click",
	    success: function(data) {
		$('#thisHourCount').text("clicked " + data.nclick + " times this second");
	    }
	})
    });


});
