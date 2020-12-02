$("#favButton").click(function(){
    $.ajax({
        type: 'POST',
        url:"/fav",
        sucess:function(response){
            console.log(reponse)
        },
        error:function(response){
            console.log(reponse)
        }
        
    })
});