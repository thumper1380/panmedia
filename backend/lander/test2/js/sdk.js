'use strict'

// Define your LeadAPI object.
var LeadAPI = (function () {
  // Define the base URL for the API.
  var BASE_URL = "/api/track/";
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0;i < cookies.length;i++) {
        var cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Define a function to send POST requests.
  function post(url, data) {
    // add csrf token to data
    data.csrfmiddlewaretoken = getCookie('csrftoken');
    return new Promise(function (resolve, reject) {
      $.ajax({
        type: "POST",
        url: BASE_URL + url,
        data: data,
        success: function (data) {
          resolve(data);
        },
        error: function (err) {
          reject(err);
        },
      });
    });
  }

  // Define a function to send GET requests.
  function get(url) {
    return $.ajax({
      type: "GET",
      url: BASE_URL + url,
      dataType: "json",
    });
  }

  // function to get p parameter from url
  function getParameterByName(name, url = window.location.href) {
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[#?&]' + name + '(=([^&#]*)|&|#|$)'),
      results = regex.exec(url);
    if (!results) return '';
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
  }


  // function initIntlTelInput(inputElementId, preferredCountries = ['us']) {
  //   var input = document.querySelector("#" + inputElementId);

  //   window.intlTelInput(input, {
  //     utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.13/js/utils.js",
  //     preferredCountries: preferredCountries,
  //     // don't show dial code next to number
  //     nationalMode: false,
  //   });
  // }

  // Define and return the public API.
  return {
    trackEvent: function (event) {
      var csrftoken = getCookie('csrftoken');
      return post("event", {
        event: event,
        p: getParameterByName('p'),
      });
    },
    pushLead: function (data) {
      return post("push/", data);
    },
    fetchLocation: function () {
      return get("locate/");
    },
    localizationData: {
      "en": {
        "first_name": "First Name",
        "last_name": "Last Name",
        "email": "Email",
        "phone_number": "Phone Number",
        "submit": "Register Now!"
      },
      "zh": {
        "first_name": "名字",
        "last_name": "姓",
        "email": "电子邮件",
        "phone_number": "电话号码",
        "submit": "立即注册！"
      },
      "es": {
        "first_name": "Nombre",
        "last_name": "Apellido",
        "email": "Correo electrónico",
        "phone_number": "Número de teléfono",
        "submit": "¡Regístrate ahora!"
      },
      "hi": {
        "first_name": "नाम",
        "last_name": "उपनाम",
        "email": "ईमेल",
        "phone_number": "फ़ोन नंबर",
        "submit": "अभी रजिस्टर करें!"
      },
      "ar": {
        "first_name": "الاسم الأول",
        "last_name": "الاسم الأخير",
        "email": "البريد الإلكتروني",
        "phone_number": "رقم الهاتف",
        "submit": "سجل الآن!"
      },
      "bn": {
        "first_name": "নাম",
        "last_name": "পদবি",
        "email": "ইমেল",
        "phone_number": "ফোন নম্বর",
        "submit": "এখনই নিবন্ধন করুন!"
      },
      "pt": {
        "first_name": "Primeiro Nome",
        "last_name": "Último Nome",
        "email": "Email",
        "phone_number": "Número de Telefone",
        "submit": "Registrar Agora!"
      },
      "ru": {
        "first_name": "Имя",
        "last_name": "Фамилия",
        "email": "Email",
        "phone_number": "Номер телефона",
        "submit": "Зарегистрироваться!"
      },
      "ja": {
        "first_name": "名",
        "last_name": "姓",
        "email": "メールアドレス",
        "phone_number": "電話番号",
        "submit": "今すぐ登録！"
      },
      "de": {
        "first_name": "Vorname",
        "last_name": "Nachname",
        "email": "E-Mail",
        "phone_number": "Telefonnummer",
        "submit": "Jetzt registrieren!"
      },
      "ms": {
        "first_name": "Nama Pertama",
        "last_name": "Nama Akhir",
        "email": "E-mel",
        "phone_number": "Nombor Telefon",
        "submit": "Daftar Sekarang!"
      },
      "fr": {
        "first_name": "Prénom",
        "last_name": "Nom de Famille",
        "email": "Email",
        "phone_number": "Numéro de Téléphone",
        "submit": "Inscrivez-vous maintenant !"
      },
      "sw": {
        "first_name": "Jina la Kwanza",
        "last_name": "Jina la Mwisho",
        "email": "Barua pepe",
        "phone_number": "Nambari ya Simu",
        "submit": "Jiandikishe Sasa!"
      },
      "vi": {
        "first_name": "Tên",
        "last_name": "Họ",
        "email": "Email",
        "phone_number": "Số Điện Thoại",
        "submit": "Đăng Ký Ngay!"
      },
      "ko": {
        "first_name": "이름",
        "last_name": "성",
        "email": "이메일",
        "phone_number": "전화번호",
        "submit": "지금 등록!"
      },
      "ta": {
        "first_name": "முதல் பெயர்",
        "last_name": "கடைசி பெயர்",
        "email": "மின்னஞ்சல்",
        "phone_number": "தொலைபேசி எண்",
        "submit": "இப்போது பதிவு செய்க!"
      },
      "tr": {
        "first_name": "Ad",
        "last_name": "Soyad",
        "email": "E-posta",
        "phone_number": "Telefon Numarası",
        "submit": "Hemen Kaydol!"
      },
      "it": {
        "first_name": "Nome",
        "last_name": "Cognome",
        "email": "Email",
        "phone_number": "Numero di Telefono",
        "submit": "Registrati Ora!"
      },
      "pl": {
        "first_name": "Imię",
        "last_name": "Nazwisko",
        "email": "Email",
        "phone_number": "Numer Telefonu",
        "submit": "Zarejestruj się!"
      },
      "uk": {
        "first_name": "Ім'я",
        "last_name": "Прізвище",
        "email": "Електронна пошта",
        "phone_number": "Номер телефону",
        "submit": "Зареєструйтесь!"
      },
      "ta-in": {
        "first_name": "முதல் பெயர்",
        "last_name": "கடைசி பெயர்",
        "email": "மின்னஞ்சல்",
        "phone_number": "தொலைபேசி எண்",
        "submit": "இப்போது பதிவு செய்க!"
      }
    },
    // Add method to localize form.
    localizeForm: function (language) {
      let data = this.localizationData[language];
      if (!data) {
        console.error("Unknown language:", language);
        return;
      }

      $("#first_name").attr("placeholder", data.first_name);
      $("#last_name").attr("placeholder", data.last_name);
      $("#email").attr("placeholder", data.email);
      $("#phone_number").attr("placeholder", data.phone_number);
      $("#submit").text(data.submit);
    },
    initIntlTelInput: function (inputElementId, preferredCountries = ['us']) {
      let input = document.querySelector("#" + inputElementId);

      window.intlTelInput(input, {
        utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/18.1.6/js/utils.js",
        preferredCountries: preferredCountries,
        excludeCountries: ['af', 'ba', 'cf', 'cd', 'cg'],
        separateDialCode: false,
      });

      input.addEventListener('keypress', function (event) {
        var key = event.key;
        if (key === 'Enter') {
          // Do nothing
        } else if (key === '+') {
          // Do nothing
        } else if (key === '-') {
          // Do nothing
        } else if (isNaN(key)) {
          event.preventDefault();
        }
      });
    },


  };


})();