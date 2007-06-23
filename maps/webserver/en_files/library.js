/*****************************************************************************\
	WEB SITE CONFIGURATION
\*****************************************************************************/

function getBaseUrl()
{
	return (document.location.href.indexOf("localhost") > -1) ? "http://localhost/guru4.net/" : "http://www.guru4.net/";
}

/*****************************************************************************\
	Common tasks
\*****************************************************************************/

// No error warning
function scriptError(msg, url, line)
{
	window.status = "ERROR: " + msg + " @ line " + line;
	return true;
}
window.onerror = scriptError;

function doLocalSearch(frm, language)
{
	if(frm.query && frm.query.value.length < 1)
	{
	    var title = "";
	    var message = "";
	    switch(language.toLowerCase())
	    {
	        case "it":
	            title = "Cerca nel sito";
	            message = "Per avviare la ricerca inserisci il testo da trovare nella casella qui a fianco";
	            break;
	        case "en":
	        default:
	            title = "Search";
	            message = "To start searching type some text in the textbox to the right";
	            break;
	            
	    }
		new Tooltip(
					"tooltip_LocalSearch",
					title,
					message,
					Tooltip.Information,
					frm.query,
					250,
					Tooltip.PositionAuto
					).show();
		frm.query.focus;
		return false;
	}
	return true;
}
function PrintPage()
{
	window.print();
}
function SendThisPage()
{
	document.location = "mailto:?subject=" + escape(document.title) + "&body=" + location.href;
}
function AddToFavorites()
{
	if(document.all)
		window.external.AddFavorite(location.href, document.title);
	else if(window.sidebar)
		window.sidebar.addPanel(document.title, location.href, "");
}
function AddToSearchProviders()
{
	if(document.all)
		window.external.AddSearchProvider("http://www.guru4.net/opensearch/searchproviderdescription.xml");
    else if ((typeof window.sidebar == "object") && (typeof
    window.sidebar.addSearchEngine == "function"))
        window.sidebar.addSearchEngine("http://www.guru4.net/opensearch/g4nmozsearch.src", "http://www.guru4.net/images/g4n_icon16.gif", "GURU4.net", "Web");
}
function SubmitFeedback(frm, language)
{
    var isRated = false;
    for(var i = 0; i < frm.rate.length; i++)
    {
        if(frm.rate[i].checked)
        {
            isRated = true;
            break;
        }
    }
    if(!isRated)
    {
        var title = "";
	    var message = "";
	    switch(language.toLowerCase())
	    {
	        case "it":
	            title = "Invia un commento";
	            message = "Prima di inviare il modulo &#232; necessario esprimere un giudizio sulla qualit&#224; del contenuto di questa pagina. Puoi anche descrivere brevemente la motivazione del tuo giudizio utilizzando la relativa casella di testo. Inoltre, se desideri essere contattato, puoi indicare il tuo indirizzo email.";
	            break;
	        case "en":
	        default:
	            title = "Send feedback";
	            message = "Before sending the form it is necessary to rate the content of this page. You can even supply a brief description of your choice using the appropriate textbox. Furthermore, if you wish to be contacted, you can supply your email address.";
	            break;
	            
	    }
        new Tooltip(
					"tooltip_SendFeedback",
					title,
					message,
					Tooltip.Exclamation,
					"pagerate",
					300,
					Tooltip.PositionAuto
					).show();
        return false;
    }
    if(frm.email.value.length > 0 && !frm.email.value.isEmail())
    {
		var title = "";
	    var message = "";
	    switch(language.toLowerCase())
	    {
	        case "it":
	            title = "Verifica email";
	            message = "Se desideri essere contattato devi indicare correttamente il tuo indirizzo email.<br />Si assicura che l'indirizzo email specificato non verr&#224; utilizzato per altri scopi.";
	            break;
	        case "en":
	        default:
	            title = "Check your email address";
	            message = "If you wish to be contacted, you must supply your email address.";
	            break;
	            
	    }
		new Tooltip(
					"tooltip_SendFeedbackBadEmail",
					title,
					message,
					Tooltip.Exclamation,
					frm.email,
					300,
					Tooltip.PositionAuto
					).show();
        return false;
    }
    frm.url.value = document.location;
    frm.action = getBaseUrl() + "tools/sendfeedback.aspx";
}

/*****************************************************************************\
	Tooltip object
\*****************************************************************************/

Tooltip = function(id, title, message, style, parentelement, width, position)
{	
	this.id = id;
	this.title = title;
	this.message = message;
	this.style = style;
	this.parentElement = (parentelement.tagName) ? parentelement : document.getElementById(parentelement);
	this.width = (width + "" == "undefined" || width == null || width + "" == "") ? null : width;
	this.position = (position + "" == "undefined" || position == null || position + "" == "") ? null : position;
	this.show = function()
	{
		removeObject(this.id);
		// create element
		var d = document.createElement("div");
		d.id = this.id;
		d.className = "tooltip";
		d.style.position = "absolute";
		if(this.width != null)
			d.style.width = this.width + "px";
		d.style.visibility = "hidden";
		// set style
		var ttbstyle = "";
		switch(this.style)
		{
			case Tooltip.Critical:
				ttbstyle = " class=\"critical\"";
				break;
			case Tooltip.Question:
				ttbstyle = " class=\"question\"";
				break;
			case Tooltip.Exclamation:
				ttbstyle = " class=\"exclamation\"";
				break;
			case Tooltip.Information:
				ttbstyle = " class=\"information\"";
				break;
		}
		// build html
		var html =  
				"<div id=\"" + this.id + "_arrow\" class=\"arrow\" style=\"display:none;\">&nbsp;</div>\
				<table border=\"0\" cellpadding=\"0\" cellspacing=\"0\" width=\"100%\"" + ttbstyle + ">\
					<tr>\
						<td class=\"tooltip_tl\">&nbsp;</td>\
						<td class=\"tooltip_t\">" + this.title + "</td>\
						<td class=\"tooltip_tr\" onclick=\"hideTooltip('" + this.id + "');\" title=\"Chiudi\"><span>chiudi</span></td>\
					</tr>\
					<tr>\
						<td class=\"content\" colspan=\"3\">" + this.message + "</td>\
					</tr>\
					<tr>\
						<td class=\"tooltip_bl\">&nbsp;</td>\
						<td class=\"tooltip_b\">&nbsp;</td>\
						<td class=\"tooltip_br\">&nbsp;</td>\
					</tr>\
				</table>";
		d.innerHTML = html;
		document.body.appendChild(d);
		// get objects
		var arrow = document.getElementById(this.id + "_arrow");
		// get sizes and positions
		var size = getElementSize(d);	
		var windowsize = getElementSize(document.body);
		var parentelementposition = getElementPosition(this.parentElement);
		var parentelementsize = getElementSize(this.parentElement);
		arrow.style.display = "block";
		var arrowsize = getElementSize(arrow);
		// set position
		if(this.position == null || this.position == Tooltip.PositionAuto)	// find best positions
		{
			// @right?
			if((windowsize.width - parentelementposition.left - parentelementsize.width - size.width - arrowsize.width) > 0 && (parentelementposition.top + parentelementsize.height / 2 - size.height / 2) > 0)
				this.position = Tooltip.PositionRight;
			// @left?
			else if((parentelementposition.left - size.width - arrowsize.width) > 0 && (parentelementposition.top + parentelementsize.height / 2 - size.height / 2) > 0)
				this.position = Tooltip.PositionLeft;
			// @top?
			else if((parentelementposition.left + parentelementsize.width / 2 - size.width / 2) > 0 && (parentelementposition.top - size.height - arrowsize.height) > 0)
				this.position = Tooltip.PositionTop;
			// @bottom (default)
			else
				this.position = Tooltip.PositionBottom;
		}
		switch(this.position)
		{
			case Tooltip.PositionRight:
				d.style.left = parentelementposition.left + parentelementsize.width + arrowsize.width + "px";
				d.style.top = parentelementposition.top + parentelementsize.height / 2 - size.height / 2 + "px";
				arrow.className = "arrow_right";
				arrowsize = getElementSize(arrow);
				arrow.style.top = size.height / 2 - arrowsize.height / 2 + "px";
				arrow.style.left = -arrowsize.width + "px";
				break;
			case Tooltip.PositionLeft:
				d.style.left = parentelementposition.left - size.width - arrowsize.width + "px";
				d.style.top = parentelementposition.top + parentelementsize.height / 2 - size.height / 2 + "px";
				arrow.className = "arrow_left";
				arrowsize = getElementSize(arrow);
				arrow.style.top = size.height / 2 - arrowsize.height / 2 + "px";
				arrow.style.left =  size.width + "px";
				break;
			case Tooltip.PositionTop:
				d.style.left = parentelementposition.left + parentelementsize.width / 2 - size.width / 2 + "px";
				d.style.top = parentelementposition.top - size.height - arrowsize.height + "px";
				arrow.className = "arrow_top";
				arrowsize = getElementSize(arrow);			
				arrow.style.top = size.height + "px";
				arrow.style.left =  size.width / 2 - arrowsize.width / 2 + "px";
				break;
			case Tooltip.PositionBottom:
				d.style.left = parentelementposition.left + parentelementsize.width / 2 - size.width / 2 + "px";
				d.style.top = parentelementposition.top + parentelementsize.height + arrowsize.height + "px";
				arrow.className = "arrow_bottom";
				arrowsize = getElementSize(arrow);
				arrow.style.top = -arrowsize.height + "px";
				arrow.style.left =  size.width / 2 - arrowsize.width / 2 + "px";
				break;
		}
		// show tooltip
		d.style.visibility = "visible";
	}
	this.hide = function()
	{
		hideTooltip(this.id);
	}
}
// tooltip - icon style
Tooltip.Critical = 16;
Tooltip.Question = 32;
Tooltip.Exclamation = 48;
Tooltip.Information = 64;

// tooltip - position style
Tooltip.PositionAuto = 0;
Tooltip.PositionTop = 1;
Tooltip.PositionRight = 2;
Tooltip.PositionBottom = 3;
Tooltip.PositionLeft = 4;

// hideTooltip: hide a tooltip
function hideTooltip(id)
{
	removeObject(id);
}

/*****************************************************************************\
	HTML DOM Utility
\*****************************************************************************/

// getElementPosition: return left and top
function getElementPosition(obj)
{
	var l = obj.offsetLeft - obj.scrollLeft;
	var t = obj.offsetTop - obj.scrollTop;
	var e = obj.offsetParent;
	while(e != null)
	{
		l += e.offsetLeft - e.scrollLeft;
		t += e.offsetTop - e.scrollTop;
		e = e.offsetParent;
	}
	return {left : l, top : t};
}

// getElementSize: return width and height
function getElementSize(obj)
{
	var w = obj.offsetWidth;
	var h = obj.offsetHeight;
	return {width : w, height : h};
}

// removeObject: remove a child node
function removeObject(id)
{
	var obj = document.getElementById(id);
	if(obj != null)
		document.body.removeChild(obj);
}

/*****************************************************************************\
	Utilities
\*****************************************************************************/

function trim()
{
	var newstr = this + "";
	newstr = newstr.lTrim();
	newstr = newstr.rTrim();
	return newstr;
}
String.prototype.trim = trim;

function lTrim()
{
	var newstr = this + "";
	while(newstr.charAt(0) == " ") 
		newstr = newstr.substring(1, newstr.length);    
	return newstr;
}
String.prototype.lTrim = lTrim;

function rTrim()
{
	var newstr = this + "";
	while(newstr.charAt(newstr.length - 1) == " ") 
		newstr = newstr.substring(0, newstr.length - 1);    
	return newstr;
}
String.prototype.rTrim = rTrim; 

function replaceText(pattern, substitute)
{
	return this.split(pattern).join(substitute);
}
String.prototype.replaceText = replaceText;

function isEmail() 
{
	var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/   
	return re.test(this);
}
String.prototype.isEmail = isEmail;
 