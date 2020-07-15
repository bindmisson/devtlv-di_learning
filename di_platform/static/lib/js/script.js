$(document).ready(function () {
    $('#submit-chapter-comment').click(function (e) {
      var text = $('#chapterCommentFormText').val(),
        url = '/discussion/chapters/' + $('#chapter-comment-form').attr('chapter-id') + '/comment/';
      postComment(url, text)
      e.preventDefault()
    })
  })
  
  
  function postComment(url, text) {
    $.ajax({
      url: url,
      type: 'POST',
      data: {
        text: text
      },
      success: function (json) {
        $('#chapterCommentFormText').val('')
        $('.chapter-comments-list').prepend(json.html)
      },
      error: function (xhr, errMsg, err) {
        alert('Something went wrong!');
        console.log(errMsg, err);
      }
    })
  }
  
  /*
  Profile picture submission
  */
  $('.profile-picture-wrapper input[type=file]').change(function () {
    $('#profile-picture-upload').submit();
  });
  
  /*
  Checking Course
  */
    $('#chapter-done').on('click', function () {
      let chapter_id = $('#chapter-done').attr('chapter-id')
      $.ajax({
        url: '/courses/completed_chapter/',
        type: 'POST',
        data: {
          chapter_id: chapter_id
        },
        success: function (json) {
          checkOrUncheck(chapter_id);
        },
        error: function (xhr, errMsg, err) {
          alert('Something went wrong!');
          console.log(errMsg, err);
        }
      })
    })
  
    function checkOrUncheck(chapter_id) {
      let button = $('#chapter-done');
      let badge = $('#status_chapter_id_' + chapter_id);
      
      if ($('#chapter-done').attr('done') == 1) {
        button.removeClass('btn-success').addClass('btn-secondary').attr('done', '0').text('Not Completed');
        badge.removeClass('badge-outline-success').addClass('badge-outline-secondary').text('Not Completed');
      } else {
        button.removeClass('btn-secondary').addClass('btn-success').attr('done', '1').text('Done');
        badge.removeClass('badge-outline-secondary').addClass('badge-outline-success').text('Done');
      }
    }
  
  /*
  CSRF management
  */
  $(function () {
    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
  
    function csrfSafeMethod(method) {
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
  
    function sameOrigin(url) {
      var host = document.location.host,
        protocol = document.location.protocol,
        sr_origin = '//' + host,
        origin = protocol + sr_origin;
      return (url == origin || url.slice(0, origin.length + 1) == origin + '/') || (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
    }
  
    $.ajaxSetup({
      beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      }
    });
  });
  
  
  
  
  
  