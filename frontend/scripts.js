const app = document.getElementById('root');

const logo = document.createElement('img');
logo.src = 'digital health 02.png';

const container = document.createElement('div');
container.setAttribute('class', 'container');

app.appendChild(logo);
app.appendChild(container);

async function build_dropdown_list() {

  const url_autocomplete_category = 'http://localhost:5000/autocomplete_category';
  const url_autocomplete_subcategory = 'http://localhost:5000/autocomplete_subcategory';
  const url_autocomplete_sex = 'http://localhost:5000/autocomplete_sex';
  const url_autocomplete_age = 'http://localhost:5000/autocomplete_age';

  var categories_array = [];
  var subcategories_array = [];
  var ages_array = [];
  var sex_array = [];

  var categories_raw = fetch(url_autocomplete_category)
                    .then(function (response) {
                        return response.json();
                    })
                    .then(function (data) {
                        return data;
                    })
                    .catch(function (err) {
                        console.log('error: ' + err);
                    });
  var subcategories_raw = fetch(url_autocomplete_subcategory)
                    .then(function (response) {
                        return response.json();
                    })
                    .then(function (data) {
                        return data;
                    })
                    .catch(function (err) {
                        console.log('error: ' + err);
                    });
  var ages_raw = fetch(url_autocomplete_age)
                    .then(function (response) {
                        return response.json();
                    })
                    .then(function (data) {
                        return data;
                    })
                    .catch(function (err) {
                        console.log('error: ' + err);
                    });
  var sex_raw = fetch(url_autocomplete_sex)
                    .then(function (response) {
                        return response.json();
                    })
                    .then(function (data) {
                        return data;
                    })
                    .catch(function (err) {
                        console.log('error: ' + err);
                    });

  await categories_raw.then(function(data) {data.forEach(x => categories_array.push(x) ) });
  await subcategories_raw.then(function(data) {data.forEach(x => subcategories_array.push(x) ) });
  await ages_raw.then(function(data) {data.forEach(x => ages_array.push(x) ) });
  await sex_raw.then(function(data) {data.forEach(x => sex_array.push(x) ) });

  var arrays = [ages_array, sex_array, categories_array, subcategories_array];
  var itemlist = ['itemslistage', 'itemslistsex', 'itemslistcat', 'itemslistsub'];

  for (var x = 0; x < arrays.length; x++) {

    var x_array = arrays[x];
    var x_list = itemlist[x];
  
    var itemsList = document.getElementById(x_list)
  
    for (var i = 0; i < x_array.length; i++) {
      var opt = x_array[i];
      var el = document.createElement("option");
    
      el.textContent = opt;
      el.value = opt;
      itemsList.appendChild(el);
    }
  }
};

build_dropdown_list();

var age_query =  document.getElementById('itemslistage');
var sex_query =  document.getElementById('itemslistsex');
var category_query =  document.getElementById('itemslistcat');
var subcategory_query =  document.getElementById('itemslistsub');

var btn = document.getElementById("btn");

btn.addEventListener("click", async function() {

    var url_query = "http://localhost:5000/query?age=" + age_query.value + 
                    "&sex=" + sex_query.value + "&clinicalindication=" +  category_query.value + 
                    "&subcategory=" + subcategory_query.value

    var output_raw = fetch(url_query)
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        return data;
    })
    .catch(function (err) {
        console.log('error: ' + err);
    });

    var output = [];

    await output_raw.then(function(data) {data.forEach(x => output.push(x) ) });

    var str = '<ul>';

    output.forEach(x => console.log(x['EXAME DE IMAGEM']));

    output.forEach(x => str += '<li>' + x['EXAME DE IMAGEM'] + '</li>');
    str += '</ul>';

    document.getElementById("outputContainer").innerHTML = str;

  });
