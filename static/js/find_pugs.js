const findCourtBtn = $('#find-court-btn')
const pugContainer = $('#pug-res-list')


function getDetails(evt){

    const btn = $(evt.target)
    const id = btn.data('id')

    window.open(`/games/${id}`, '__blank').focus()
}

function generateGameMarkUp(game){
    return `
<div class="list-group-item list-group-item position-relative">
    <div class="d-flex justify-content-between ps-5" id="game-header">
        <h6 class="mb-1">${game.date}@ ${game.time}</h6>
        <img src="/static/profile_pics/${game.creator_img_file}" alt="" class="position-absolute top-50 start-0 translate-middle translate-middle rounded-circle shadow" height="75px" width="75px">
    </div>
    <div>
        <h5 class="ps-5">${game.title}</h5>
        <p class="ps-5">${game.city}, ${game.state}</p>
    </div>
    <div class="d-flex justify-content-between ps-5" id="button container">
        <small class="">${game.members} Attendees</small>
        <button class="btn btn-outline-success" data-id="${game.id}">see details</button>
    </div>
</div>
    `
}

function addUsername(game, gameMarkUp){
    const usernameMarkup = `<a class="text-decoration-none" href="users/${game.creator_id}"><small>@${game.creator_username}</small></a>`
    if (game.creator_username){
        const container = $(gameMarkUp).find('#game-header');
        container.append(usernameMarkup)
    }
    return 
}


async function showGames(evt){
    evt.preventDefault()

   
    const city = $('#city').val()
    const state = $('#state').val()

    data = {
        city,
        state
    }

    const res = await axios.post(`/api/games`, json=data )
    const games = res.data.games

    for(let game of games){
        let newGame = $(generateGameMarkUp(game));
        pugContainer.append(newGame);
        addUsername(game, newGame)
    }

    pugContainer.on('click', "button", getDetails)



}

findCourtBtn.click(showGames)