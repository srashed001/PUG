
$('.join-game').click(joinGame)

async function joinGame(evt){
    
    const id = evt.target.id;
    console.log(id);
    await axios.post(`/games/${id}`);

    location.reload(true);

}

$('.leave-game').click(leaveGame)

async function leaveGame(evt){
    
    const id = evt.target.id;
    console.log(id);
    await axios.delete(`/games/${id}`);

    location.reload(true);


}



