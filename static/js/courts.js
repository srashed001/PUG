
let PageTokens = []
let currCity = ""
let currState = ""

console.log(PageTokens)

function generateErrorMarkUp(resp){
    const error = resp.data.error

    return `
    <div class="list-group-item">
        <h3 class="text-danger">${error}</h3> 
    </div>`
}


function generateCourtHTML(court){
    return `
    <div class="list-group-item">
        <div class="d-flex justify-content-between">
            <h6>${court.name}</h6>
            <p>${court.address}</p>
        </div>
        <div class="d-flex justify-content-between">
            <a href="/courts/game/${court.id}" class="btn btn-outline-success">
                create pug
            </a>
            <small>${court.rating}</small>
        </div>     
    </div>
    `;
}

function generateNextPageButtonHTML(page){

    return `
    <button class="btn btn-outline-secondary" id="next-page" data-page="${page}">next page</button>
    `
}

function generateCourtMarkUp(resp){

    if(resp.data.error){
        const errorMarkup = $(generateErrorMarkUp(resp))
        $('#court-res-list').append(errorMarkup)
        return 
    }

    let nextPageButton
    let pgTokenAvailable = false

    let courts = resp.data.data


    if(courts.length === 2){
        pgTokenAvailable = true;
        const pageTokenData = courts[0]
        const pageToken = pageTokenData[0];
        PageTokens.push(pageToken)
        nextPageButton = $(generateNextPageButtonHTML(PageTokens.length - 1))
        courts = courts[1]
    }


    for (let court of courts){
        let newCourt = $(generateCourtHTML(court))
        $('#court-res-list').append(newCourt)
    };
    
    $('#next-pg-container').empty()
    if(pgTokenAvailable === true){
        $('#next-pg-container').append(nextPageButton);
        $('#next-page').click(getNextOrPrevPage);
    } 
}

async function get_courts(evt){
    
    evt.preventDefault()
    
    data = {
        "city" : $("#city").val(),
        "state" : $("#state").val(),
    };

    const resp = await axios.post("/api/courts", json=data);

    console.log(resp)
    
    $('#court-res-list').empty()
    generateCourtMarkUp(resp)

};



async function getNextOrPrevPage(evt){


    const button = $(evt.target)
    const tokenIndex = button.data('page')
    console.log(tokenIndex)
    const pageToken = PageTokens[tokenIndex]

    console.log(pageToken)


    data = {
        "pageToken": pageToken
    }

    const resp = await axios.post("/api/courts/next", json=data);
    console.log(resp)

    generateCourtMarkUp(resp)

    

};

$('#find-court-btn').click(get_courts);
