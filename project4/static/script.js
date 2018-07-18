var timeoutID;
var timeout = 1000;
var cats;
var purchases;

function setup() {
	document.getElementById("theButton").addEventListener("click", addCategory, true);
	document.getElementById("purchaseButton").addEventListener("click", addPurchase, true);

	poller();
	poller1();
}

function makeReq(method, target, retCode, action, data) {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	httpRequest.onreadystatechange = makeHandler(httpRequest, retCode, action);
	httpRequest.open(method, target);
	
	if (data){
		httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		httpRequest.send(data);
	}
	else {
		httpRequest.send();
	}
}

function makeHandler(httpRequest, retCode, action) {
	function handler() {
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
			if (httpRequest.status === retCode) {
				console.log("recieved response text:  " + httpRequest.responseText);
				action(httpRequest.responseText);
			} else {
				alert("There was a problem with the request.  you'll need to refresh the page!");
			}
		}
	}
	return handler;
}

function addCategory() {
	var newCat = document.getElementById("newCat").value
	var budget = document.getElementById("budget").value
	var data;
	data = "name=" + newCat + "&budget=" + budget;
	window.clearTimeout(timeoutID);
	makeReq("POST", "/categories", 201, poller, data);
	document.getElementById("newCat").value = "New Category";
}

function addPurchase() {
	var newPurchase = document.getElementById("newPurchase").value
	var amount = document.getElementById("amount").value
	var cat = document.getElementById("cat").value
	var date = document.getElementById("date").value
	
	var data;
	data = "name=" + newPurchase + "&amount=" + amount + "&cat=" + cat + "&date=" + date;
	window.clearTimeout(timeoutID);
	makeReq("POST", "/purchases", 201, poller1, data);
	document.getElementById("newCat").value = "New Purchase";
}

function poller() {
	makeReq("GET", "/categories", 200, repopulate);
}

function poller1() {
	makeReq("GET", "/purchases", 200, repopulate1);
}

function deleteCategory(taskID) {
	makeReq("DELETE", "/categories/" + taskID, 204, poller);
}

function deletePurchase(taskID) {
	makeReq("DELETE", "/purchases/" + taskID, 204, poller1);
}

// helper function for repop:
function addCell(row, text) {
	var newCell = row.insertCell();
	var newText = document.createTextNode(text);
	newCell.appendChild(newText);
}

function addRemainingCell(row, text) {
	var newCell = row.insertCell();
	newCell.className = 'remaining';
	var newText = document.createTextNode(text);
	newCell.appendChild(newText);
}

function repopulate(responseText) {
	cats = JSON.parse(responseText);
	console.log("cats: ", cats);
	var tab = document.getElementById("theTable");
	var newRow, newCell, t, task, newButton, newDelF;

	while (tab.rows.length > 0) {
		tab.deleteRow(0);
	}

	newRow = tab.insertRow();
	addCell(newRow, "Category");
	addCell(newRow, "Budget");
	addCell(newRow, "Remaining");
	console.log("cats now: ", cats);
	for (c in cats) {
		newRow = tab.insertRow();
		addCell(newRow, cats[c].name);
		addCell(newRow, '$'+cats[c].budget);
		addRemainingCell(newRow, "");
				
		newCell = newRow.insertCell();
		newButton = document.createElement("input");
		newButton.type = "button";
		newButton.value = "Delete " + cats[c].name;
		(function(_c){ newButton.addEventListener("click", function() { deleteCategory(cats[_c].cat_id); }); })(c);
		newCell.appendChild(newButton);
	}
	budget();
	//timeoutID = window.setTimeout(poller, timeout);
}

function repopulate1(responseText) {
	purchases = JSON.parse(responseText);
	console.log("purchases: ", purchases);
	var tab = document.getElementById("purchaseTable");
	var newRow, newCell, t, task, newButton, newDelF;

	while (tab.rows.length > 0) {
		tab.deleteRow(0);
	}

	newRow = tab.insertRow();
	addCell(newRow, "Item");
	addCell(newRow, "Amount");
	addCell(newRow, "Category");
	addCell(newRow, "Date");
	console.log("purchases now: ", purchases);
	for (p in purchases) {
		newRow = tab.insertRow();
		addCell(newRow, purchases[p].name);
		addCell(newRow, '$'+purchases[p].amount);
		addCell(newRow, purchases[p].cat);
		addCell(newRow, purchases[p].date);
		
		newCell = newRow.insertCell();
		newButton = document.createElement("input");
		newButton.type = "button";
		newButton.value = "Delete " + purchases[p].name;
		(function(_p){ newButton.addEventListener("click", function() { deletePurchase(purchases[_p].purchase_id); }); })(p);
		newCell.appendChild(newButton);
	}
	budget();
	//timeoutID = window.setTimeout(poller, timeout);
}

function budget() {
	if (typeof cats === undefined) {
		return;
	}
	if (typeof purchases === undefined) {
		return;
	}
	var i = 0;
	var catNames = [];
	cats.forEach(function(e) {
		e.remaining = e.budget;
		purchases.map(x => e.remaining = x.cat === e.name ? e.remaining -= x.amount : e.remaining);
		document.querySelectorAll(".remaining")[i++].innerHTML='$'+e.remaining;
		catNames.push(e.name);
	});
	var spent = 0;
	purchases.map(x => spent = catNames.indexOf(x.cat) === -1 ? spent += x.amount : spent);
	document.getElementById("spent").innerHTML="Uncategorized Expenditures: $" + spent;
}

// setup load event
window.addEventListener("load", setup, true);