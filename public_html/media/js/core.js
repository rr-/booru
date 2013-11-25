function setCookie(name, value, exdays)
{
	var exdate = new Date();
	exdate.setDate(exdate.getDate() + exdays);
	value = escape(value) + '; path=/' + ((exdays == null) ? '' : '; expires=' + exdate.toUTCString());
	document.cookie = name + '=' + value;
}

function getCookie(name)
{
	console.log(document.cookie);
	var value = document.cookie;
	var start = value.indexOf(' ' + name + '=');

	if (start == -1)
		start = value.indexOf(name + '=');

	if (start == -1)
		return null;

	start = value.indexOf('=', start) + 1;
	var end = value.indexOf(';', start);
	if (end == -1)
		end = value.length;

	return unescape(value.substring(start, end));
}

function rememberLastSearchQuery()
{
	//lastSearchQuery variable is obtained from layout
	setCookie('last-search-query', lastSearchQuery);
}

//core functionalities, prototypes
$.fn.hasAttr = function(name)
{
	return this.attr(name) !== undefined;
};

if ($.when.all === undefined)
{
	$.when.all = function(deferreds)
	{
		var deferred = new $.Deferred();
		$.when.apply($, deferreds).then(function()
		{
			deferred.resolve(Array.prototype.slice.call(arguments, 0));
		}, function()
		{
			deferred.fail(Array.prototype.slice.call(arguments, 0));
		});

		return deferred;
	}
}



//safety trigger
$(function()
{
	$('.safety a').click(function(e)
	{
		e.preventDefault();

		var aDom = $(this);
		if (aDom.hasClass('inactive'))
			return;
		aDom.addClass('inactive');

		var url = $(this).attr('href') + '?json';
		$.get(url).always(function(data)
		{
			if (data['success'])
				window.location.reload();
			else
			{
				alert(data['message'] ? data['message'] : 'Fatal error');
				aDom.removeClass('inactive');
			}
		});
	});
});



//basic event listeners
$(function()
{
	$('body').bind('dom-update', function()
	{
		//event confirmations
		function confirmEvent(e)
		{
			if (!confirm($(this).attr('data-confirm-text')))
			{
				e.preventDefault();
				e.stopPropagation();
			}
		}

		$('form[data-confirm-text]').submit(confirmEvent);
		$('a[data-confirm-text]').click(confirmEvent);


		//simple action buttons
		$('a.simple-action').click(function(e)
		{
			if(e.isPropagationStopped())
				return;

			e.preventDefault();
			rememberLastSearchQuery();

			var aDom = $(this);
			if (aDom.hasClass('inactive'))
				return;
			aDom.addClass('inactive');

			var url = $(this).attr('href') + '?json';
			$.get(url, {submit: 1}).always(function(data)
			{
				if (data['success'])
				{
					if (aDom.hasAttr('data-redirect-url'))
						window.location.href = aDom.attr('data-redirect-url');
					else if (aDom.data('callback'))
						aDom.data('callback')();
					else
						window.location.reload();
				}
				else
				{
					alert(data['message'] ? data['message'] : 'Fatal error');
					aDom.removeClass('inactive');
				}
			});
		});


		//attach data from submit buttons to forms before .submit() gets called
		$(':submit').each(function()
		{
			$(this).click(function()
			{
				var form = $(this).closest('form');
				form.find('.faux-submit').remove();
				var input = $('<input class="faux-submit" type="hidden"/>').attr({
					name: $(this).attr('name'),
					value: $(this).val()
				});
				form.append(input);
			});
		});
	});


	//try to remember last search query
	window.onbeforeunload = rememberLastSearchQuery;
});



//modify DOM on small viewports
function processSidebar()
{
	$('#inner-content .unit').addClass('bottom-unit');
	if ($('body').width() < 600)
	{
		$('body').addClass('small-screen');
		$('#sidebar').insertAfter($('#inner-content'));
		$('#sidebar .unit').removeClass('left-unit').addClass('bottom-unit');
	}
	else
	{
		$('body').removeClass('small-screen');
		$('#sidebar').insertBefore($('#inner-content'));
		$('#sidebar .unit').removeClass('bottom-unit').addClass('left-unit');
	}
}
$(function()
{
	$(window).resize(function()
	{
		if ($('body').width() == $('body').data('last-width'))
			return;
		$('body').data('last-width', $('body').width());
		$('body').trigger('dom-update');
	});
	$('body').bind('dom-update', processSidebar);
});



//autocomplete
function split(val)
{
    return val.split(/\s+/);
}

function extractLast(term)
{
    return split(term).pop();
}

$(function()
{
	$('.autocomplete').each(function()
	{
		var searchInput = $(this);
		searchInput
		// don't navigate away from the field on tab when selecting an item
		.bind('keydown', function(event)
		{
			if (event.keyCode === $.ui.keyCode.TAB && $(this).data('autocomplete').menu.active)
			{
				event.preventDefault();
			}
		}).autocomplete({
			minLength: 1,
			position:
			{
				my: 'right top',
				at: 'right bottom'
			},
			source: function(request, response)
			{
				var term = extractLast(request.term);
				if (term != '')
					$.get(searchInput.attr('data-autocomplete-url') + '?json', {filter: term + ' order:popularity,desc'}, function(data)
					{
						response($.map(data.tags, function(tag) { return { label: tag.name + ' (' + tag.count + ')', value: tag.name }; }));
					});
			},
			focus: function()
			{
				// prevent value inserted on focus
				return false;
			},
			select: function(event, ui)
			{
				var terms = split(this.value);
				terms.pop();
				terms.push(ui.item.value);
				terms.push('');
				this.value = terms.join(' ');
				return false;
			}
		});
	});
});

function getTagItOptions()
{
	return {
		caseSensitive: false,
		autocomplete:
		{
			source:
				function(request, response)
				{
					var term = request.term.toLowerCase();
					var tags = $.map(this.options.availableTags, function(a)
					{
						return a.name;
					});
					var results = $.grep(tags, function(a)
					{
						if (term.length < 3)
							return a.toLowerCase().indexOf(term) == 0;
						else
							return a.toLowerCase().indexOf(term) != -1;
					});
					results = results.slice(0, 15);
					if (!this.options.allowDuplicates)
						results = this._subtractArray(results, this.assignedTags());
					response(results);
				},
		}
	};
}



//hotkeys
$(function()
{
	Mousetrap.bind('q', function() { $('#top-nav input').focus(); return false; }, 'keyup');
	Mousetrap.bind('w', function() { $('body,html').animate({scrollTop: '-=150px'}, 200); });
	Mousetrap.bind('s', function() { $('body,html').animate({scrollTop: '+=150px'}, 200); });
	Mousetrap.bind('a', function() { var url = $('.paginator:visible .prev:not(.disabled) a').attr('href'); if (typeof url !== 'undefined') window.location.href = url; }, 'keyup');
	Mousetrap.bind('d', function() { var url = $('.paginator:visible .next:not(.disabled) a').attr('href'); if (typeof url !== 'undefined') window.location.href = url; }, 'keyup');
	Mousetrap.bind('p', function() { $('.post a').eq(0).focus(); return false; }, 'keyup');
});
