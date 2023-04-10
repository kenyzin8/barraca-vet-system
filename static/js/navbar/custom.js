$(document).ready(function () {
    $(window).scroll(function () {
      if ($(this).scrollTop() > 0) {
        $(".navbar").addClass("scrolled");
      } else {
        $(".navbar").removeClass("scrolled");
      }
    });
  });