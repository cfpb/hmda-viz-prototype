/**
	* get data for each select input
	* call the corresponding mustache template and fill the input
	* set the first option as selected
	*/
function getUIData() {
	'use strict';
  $('select').each(function() {
    var selectID = this.id;
    // get <select> data
    $.get(selectID + '.json', function(data) {
    	// get template
      $.get('/hmda-viz-prototype/templates/selects.html', function(templates) {
        var template = $(templates).filter('#' + selectID).html();
        var html = Mustache.to_html(template, data);
        $('#' + selectID).html(html);
        // set first option as selected
        $('#' + selectID + ' option:first').attr('selected', 'selected');
      });
    });
  });
}

/**
	* get data for the table
	* call the corresponding mustache template and fill the input
	* set the first option as selected
	*/
function getTableData(table) {
	'use strict';
	// get <table> data
  $.get(table + '.json', function(data) {
  	// get template
    $.get('/hmda-viz-prototype/templates/' + table + '.html', function(templates) {
      var template = $(templates).filter('#' + table).html();
      var html = Mustache.to_html(template, data);
      $('#' + table).html(html);
    });
  });
}

/** 
	* update the button link on the form pages
	*/
function setLink() {
	'use strict';
  var newURL = '';  // needed on first page, year and state make the url
  $('select').each(function() {
    newURL += $(this).val().replace(' ', '-').toLowerCase() + '/';
  });
  $('.js-btn').attr('href', newURL);
}

$( document ).ready(function() {
	'use strict';
  jQuery.ajaxSetup({async:false});  // no async!

  var urlPath = window.location.pathname.split('/');
  var path = urlPath[urlPath.length-2];

  if (urlPath.length === 8) {
    getTableData(path);
  } else {
    // fill the select inputs
    getUIData();
    // initial set link
    setLink();
    // call setlink when new choice is made
    $('select').click(function() {
      setLink();
    });
  }
});