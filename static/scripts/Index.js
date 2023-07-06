var images = [];

console.log('111111111111111111111111111')
images[0] = "../static/Assets/v1_12.png"
images[1] = "../static/Assets/IMG_20230513_200148_338.jpg"
images[2] = "../static/Assets/IMG_20230513_200149_568.jpg"

var index = 1;

function change() {
    setInterval(() => {
        document.getElementById("image1").src = images[index]
        if(index === 2){
            index = 0;
        }else{
            index++ ;
        }
    }, 3000);
}

window.onload = () => {
    setTimeout(change() , 1000)
}

function show() {
    document.getElementById('burger1').style.visibility = "visible";
}
function hide() {
    document.getElementById('burger1').style.visibility = "hidden";
}
