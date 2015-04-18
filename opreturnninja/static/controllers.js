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
})();