$(".DOM-queryButton").click(function(e) {
    sent_object = {q: e.currentTarget.id};

    $.ajax({
        type: "GET",
        url: "/_query",
        dataType: 'json',
        data: sent_object,
        success: function(data) {
            $('#DOM-responseQuery').html(data.response.response_str);
        }
    });
});


function clean_query_response() {
    $('#DOM-responseQuery').html('&nbsp;<br>');
}