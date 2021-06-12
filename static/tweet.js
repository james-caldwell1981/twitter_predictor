$('#author_submit').click(function(){
    $.ajax({
        url: '/add_author?twitter_handle=' + $('#author_name_input').val(),
        method: 'POST',
        success: function (data) {
            $('#response_name').text(data.response_name)
            $('#response_body').text(data.response_body)
            $('#author_name_input').val('')
        }
    });
});

$('#tweet_submit').click(function (){
    $.ajax({
        url: '/predict_author?tweet_to_classify=' + $('#tweet_text_input').val(),
        method: 'POST',
        success: function (data) {
            $('#response_name').text(data.response_name)
            $('#response_body').text(data.response_body)
            $('#author_name_input').val('')
        }
    });
});
