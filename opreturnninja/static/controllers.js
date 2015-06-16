(function(){
    var app = angular.module('opreturn-ninja', []);

    app.controller('TxPushController', ['$http', '$log', function($http, $log){
        var pusher = this;

        pusher.tx = '';

        pusher.msg = '';
        pusher.showMsg = false;
        pusher.loading = false;

        pusher.push = function(){
            pusher.showMsg = false;
            pusher.loading = true;
            $http.post('/api', {jsonrpc:"1.0", id:"", method:"sendrawtransaction", params:[pusher.tx]}).
            success(function(data){
                pusher.msg = data;
                pusher.showMsg = true;
                pusher.loading = false;
            }).error(function(error,and,other,things){
                $log.log(error);
                pusher.loading = false;
                pusher.msg = error;
                pusher.showMsg = true;
            });
        };
    }]);

    app.controller('TabController', ['$http', '$log', '$location', function($http, $log, $location){
        var tabs = this;

        var current = 'main';
        $location.hash(current);

        tabs.is = function(tabName){
            return current == tabName;
        };

        tabs.set = function(tabName){
            current = tabName;
            $location.hash(tabName);
        };
    }]);

    app.config(function($locationProvider) {
        $locationProvider.html5Mode({enabled: true}).hashPrefix('!');
    });
})();