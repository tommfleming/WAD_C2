$(function () {
    $('.like').click(function () {
      ratePost(this, 'LIKE');
    });
    $('.dislike').click(function () {
      ratePost(this, 'DISLIKE');
    });
  });
  
  function ratePost(caller, action) {
    var postId = caller.parentElement.getAttribute('postid');
    $.ajax({
      type: "POST",
      url: "/rate",
      contentType: "application/json",
      data: JSON.stringify({ action: action, post_id: postId }),
      success: function (response) {
        alert(response.message);
      },
      error: function (xhr) {
        alert(`Error: ${xhr.responseJSON.error}`);
      }
    });
  }
  