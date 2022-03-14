$(document).ready(function() {
    'use strict';
    // Adjusting the session's iframe sizes
    var iframe = document.getElementById("iframe_session");
    if (iframe){
        iframe.onload = function(){
            var height = iframe.contentWindow.document.body.scrollHeight + 25;
            iframe.style.height = height + 'px';
            iframe.style.width = '100%';
        }
    }

//    // Fire alert for disconnectForm
//	$('#disconnectForm').on('click',function(e){
//        var form = $(this).parents('form');
//        console.log(form)
//        var provider = $(this).val();
//        Swal.fire({
//            title: django.gettext('Disconnect account from '+provider+'. '+'Are you sure?'),
//            icon: 'warning',
//            showCancelButton: true,
//            cancelButtonText: django.gettext('No, cancel!'),
//            cancelButtonColor: '#d33',
//            confirmButtonText: django.gettext('Yes, disconnect me!'),
//            confirmButtonColor: '#3085d6',
//        }).then((result) => {
//            if (result.value) {
//                form.submit();
//                let timerInterval
//                Swal.fire({
//                  title:  django.gettext('Disconnected!'),
//                  icon: 'success',
//                  title: django.gettext('Your user has been disconnected!'),
//                  html: django.gettext('Redirect in <b></b> milliseconds.'),
//                  timer: 2000,
//                  timerProgressBar: true,
//                  didOpen: () => {
//                    Swal.showLoading()
//                    const b = Swal.getHtmlContainer().querySelector('b')
//                    timerInterval = setInterval(() => {
//                      b.textContent = Swal.getTimerLeft()
//                    }, 100)
//                  },
//                  willClose: () => {
//                    clearInterval(timerInterval)
//                  }
//                }).then((result) => {
//                  if (result.dismiss === Swal.DismissReason.timer) {
//                    console.log('Closed by the timer')
//                  }
//                })
//            }
//        });
//    });

    // Fire alert for deleteForm
    $('#deleteForm').on('click',function(e){
        e.preventDefault();
        var form = $(this).parents('form');
        Swal.fire({
            title: django.gettext('Delete account and all data. Are you sure?'),
            text: django.gettext("You won't be able to revert this!"),
            icon: 'warning',
            showCancelButton: true,
            cancelButtonText: django.gettext('No, cancel!'),
            cancelButtonColor: '#d33',
            confirmButtonText: django.gettext('Yes, delete my user!'),
            confirmButtonColor: '#3085d6',
        }).then((result) => {
            if (result.value) {
                form.submit();
                let timerInterval
                Swal.fire({
                  title:  django.gettext('Deleted!'),
                  icon: 'success',
                  title: django.gettext('Your user has been deleted!'),
                  html: django.gettext('Redirect in <b></b> milliseconds.'),
                  timer: 2000,
                  timerProgressBar: true,
                  didOpen: () => {
                    Swal.showLoading()
                    const b = Swal.getHtmlContainer().querySelector('b')
                    timerInterval = setInterval(() => {
                      b.textContent = Swal.getTimerLeft()
                    }, 100)
                  },
                  willClose: () => {
                    clearInterval(timerInterval)
                  }
                }).then((result) => {
                  if (result.dismiss === Swal.DismissReason.timer) {
                    console.log('Closed by the timer')
                  }
                })
            }
        });
    });
});

//	<script>
//
//	$('#login').on('click',function(e){
//		Swal.fire({
//		  title: 'Login!',
//		  html:
//			'I will close in <strong></strong> seconds.<br/><br/>' +
//			'<button id="increase" class="btn btn-warning">' +
//			  'I need 5 more seconds!' +
//			'</button><br/><br/>' +
//			'<button id="stop" class="btn btn-danger">' +
//			  'Please stop the timer!!' +
//			'</button><br/><br/>' +
//			'<button id="resume" class="btn btn-success" disabled>' +
//			  'Phew... you can restart now!' +
//			'</button><br/><br/>' +
//			'<button id="toggle" class="btn btn-primary">' +
//			  'Toggle' +
//			'</button>',
//		  didOpen: () => {
//			const content = Swal.getHtmlContainer()
//			const $ = content.querySelector.bind(content)
//
//			const google = $('#google')
//			const twitter = $('#twitter')
//
//			Swal.showLoading()
//
//			google.addEventListener('click', () => {
//			  Swal.stopTimer()
//			})
//
//			twitter.addEventListener('click', () => {
//			  Swal.resumeTimer()
//			})
//
//		  },
//		})
//    });
//
//	$('#twitter-button').on('click',function(e){
//        e.preventDefault();
//        var url = $(this).value;
//        Swal.fire({
//            title: django.gettext('Delete account and all data. Are you sure?'),
//            html: '<div id="test_frame"></>div>',
//            icon: 'warning',
//			didOpen: () => {
//				grecaptcha.render('recaptcha', {
//				  'sitekey': '6LdvplUUAAAAAK_Y5M_wR7s-UWuiSEdVrv8K-tCq'
//				})
//			  },
//        }).then((result) => {
//            if (result.value) {
//                let timerInterval
//                Swal.fire({
//                  title:  django.gettext('Deleted!'),
//                  icon: 'success',
//                  title: django.gettext('Your user has been deleted!'),
//                  html: django.gettext('Redirect in <b></b> milliseconds.'),
//                  timer: 2000,
//                  timerProgressBar: true,
//                  didOpen: () => {
//                    Swal.showLoading()
//                    const b = Swal.getHtmlContainer().querySelector('b')
//                    timerInterval = setInterval(() => {
//                      b.textContent = Swal.getTimerLeft()
//                    }, 100)
//                  },
//                  willClose: () => {
//                    clearInterval(timerInterval)
//                  }
//                }).then((result) => {
//                  if (result.dismiss === Swal.DismissReason.timer) {
//                    console.log('Closed by the timer')
//                  }
//                })
//            }
//        });
//    });
//
//	</script>
//
////on click
//// call Swal.fire({title: 'Confirm', text:'Do you want to continue?'})
//// if result.isConfirmed trigger confirmed
//function delete_account(){
//    // Show messages inside bootstrap alerts
//    Swal.fire({
//      title: 'Are you sure?',
//      text: "You won't be able to revert this!",
//      icon: 'warning',
//      showCancelButton: true,
//      cancelButtonText: 'No, cancel!',
//      cancelButtonColor: '#d33',
//      confirmButtonText: 'Yes, delete it!',
//      confirmButtonColor: '#3085d6',
//    }).then((result) => {
//      if (result.isConfirmed) {
//        trigger confirmed
//        Swal.fire(
//          'Deleted!',
//          'Your file has been deleted.',
//          'success'
//        )
//      }
//    })
//}
