$(document).ready(function() {
    'use strict';

    Swal.fire({
      title: 'Login!',
      html:
        'I will close in <strong></strong> seconds.<br/><br/>' +
        '<button id="increase" class="btn btn-warning">' +
          'I need 5 more seconds!' +
        '</button><br/><br/>' +
        '<button id="stop" class="btn btn-danger">' +
          'Please stop the timer!!' +
        '</button><br/><br/>' +
        '<button id="resume" class="btn btn-success" disabled>' +
          'Phew... you can restart now!' +
        '</button><br/><br/>' +
        '<button id="toggle" class="btn btn-primary">' +
          'Toggle' +
        '</button>',
      didOpen: () => {
        const content = Swal.getHtmlContainer()
        const $ = content.querySelector.bind(content)

        const google = $('#google')
        const twitter = $('#twitter')

        Swal.showLoading()

        google.addEventListener('click', () => {
          Swal.stopTimer()
        })

        twitter.addEventListener('click', () => {
          Swal.resumeTimer()
        })

      },
    })

//Swal.fire({
//  title: 'Submit your Github username',
//  input: 'text',
//  inputAttributes: {
//    autocapitalize: 'off'
//  },
//  showCancelButton: true,
//  confirmButtonText: 'Look up',
//  showLoaderOnConfirm: true,
//  preConfirm: (login) => {
//    return fetch(`//api.github.com/users/${login}`)
//      .then(response => {
//        if (!response.ok) {
//          throw new Error(response.statusText)
//        }
//        return response.json()
//      })
//      .catch(error => {
//        Swal.showValidationMessage(
//          `Request failed: ${error}`
//        )
//      })
//  },
//  allowOutsideClick: () => !Swal.isLoading()
//}).then((result) => {
//  if (result.isConfirmed) {
//    Swal.fire({
//      title: `${result.value.login}'s avatar`,
//      imageUrl: result.value.avatar_url
//    })
//  }
//})

//    const Toast = Swal.mixin({
//      toast: true,
//      position: 'top-end',
//      showConfirmButton: false,
//      timer: 3000,
//      timerProgressBar: true,
//      didOpen: (toast) => {
//        toast.addEventListener('mouseenter', Swal.stopTimer)
//        toast.addEventListener('mouseleave', Swal.resumeTimer)
//      }
//    })
//    Toast.fire({
//      icon: 'success',
//      title: 'Signed in successfully'
//    })


    var $validationModal, $emailRequired;

    modalDialog('#livejournal-modal', 'livejournal');
    modalDialog('#openid-modal', 'openid');
    modalDialog('#email-modal', 'email');
    modalDialog('#username-modal', 'username');
    $validationModal = modalDialog('#validation-sent-modal');
    $emailRequired = modalDialog('#email-required-modal');

    modalDialog('#ajax-login-modal', 'ajax-login', function (event) {
      var $backend, $accessToken, $accessTokenSecret, $fields, $result;
      event.preventDefault();

      $modal = $(this).closest('.modal');
      $form = $modal.find('form');
      $backend = $modal.find('[name="backend"]');
      $accessToken = $modal.find('[name="access_token"]');
      $accessTokenSecret = $modal.find('[name="access_token_secret"]');
      $result = $modal.find('.login-result');

      $.get('/ajax-auth/' + $backend.val() + '/', {
        access_token: $accessToken.val(),
        access_token_secret: $accessTokenSecret.val(),
      }, function (data, xhr, response) {
        $result.find('.user-id').html(data.id);
        $result.find('.user-username').html(data.username);
        $form.hide();
        $result.show();
        setTimeout(function () { window.location = '/'; }, 10000);
      }, 'json')
    });

    modalDialog('#persona-modal', 'persona', function (event) {
      var $form;
      event.preventDefault();

      $form = $(this).closest('form');
      navigator.id.get(function (assertion) {
        if (assertion) {
          $form.find('[name="assertion"]').val(assertion)
          $form.submit();
        } else {
          alert('An error occurred while getting your assertion, try again.');
        }
      });
    });

    $('.disconnect-form').on('click', 'a.btn', function (event) {
      event.preventDefault();
      $(event.target).closest('form').submit();
    });

});
