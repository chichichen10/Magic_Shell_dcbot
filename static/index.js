const handleCommand = () =>{
            console.log('clicked')
            online = false
            fetch('https://dashboard.chichichen.xyz', {
    method: 'post',
    headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
      },body: JSON.stringify({
         command: document.getElementById('command').value})}).then( res=>{console.log(res);
                                                                          window.location.reload()})
        }
        setInterval(function() {
    fetch('/online_status')
      .then(response => response.json())
      .then(data => {
        // 更新在线状态变量的值
        var onlineText = data.online ? 'Online' : 'Offline';
        var onlineClass = data.online ? 'is-success' : 'is-danger';

        // 将在线状态信息显示在 HTML 中
        document.getElementById('status').innerHTML = onlineText;
        document.getElementById('status').classList.remove('is-success', 'is-danger');
        document.getElementById('status').classList.add(onlineClass);
      });
  }, 5000); // 每隔 5 秒更新一次在线状态