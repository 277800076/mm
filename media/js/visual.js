$(function () {
    ani1Out();
    ani2Out();
    ani3Out();
    ani4Out();
    ani1In();

    $(".featured").tabs({ fx: { opacity: 'toggle', duration: 100} }).tabs('rotate', 6000, true)
    $(".featured").bind("tabsshow", function (e, tab) { animating(tab); });
    $("#stopStartTabs").toggle(function () { stopTabs(); }, function () { startTabs(); })
    $("#prevTabs").bind("click", function () { prevTabs() });
    $("#nextTabs").bind("click", function () { nextTabs() });

});

function stopTabs() {
    $("#stopStartTabs").css("background-position", "-22px 0");
    $(".featured").tabs('rotate', 0, false)
}
function startTabs() {
    $("#stopStartTabs").css("background-position", "-22px -22px");
    $(".featured").tabs('rotate', 7000, true)
}
function prevTabs() {
    var selected = $(".featured").tabs("option", "selected");
    if (selected == 0) selected = 4;
    $(".featured").tabs("option", "selected", selected - 1);
}
function nextTabs() {
    var selected = $(".featured").tabs("option", "selected");
    if (selected == 3) selected = -1;
    $(".featured").tabs("option", "selected", selected + 1);
}

function animating(tab) {
    if (tab.index == 0) {
        ani2Out();
        ani3Out();
        ani4Out();
        ani1In();
    }

    if (tab.index == 1) {
        ani1Out();
        ani3Out();
        ani4Out();
        ani2In();
    }

    if (tab.index == 2) {
        ani1Out();
        ani2Out();
        ani4Out();
        ani3In();
    }
    if (tab.index == 3) {
        ani1Out();
        ani2Out();
        ani3Out();
        ani4In();
    }
}


function ani1In() {
    $(".b-one").transition({ x: '0px', y: '150px', opacity: 1, delay: 0 });
    $(".b-two").transition({ x: '100px', y: '0', opacity: 1, delay: 100 });
    $(".b-three").transition({ x: '100px', y: '0', opacity: 1, delay: 200 });
    $(".b-four").transition({ x: '100px', y: '0', opacity: 1, delay: 300 });
    $(".b-five").transition({ x: '100px', y: '0', opacity: 1, delay: 400 });
    $(".b-six").transition({ opacity: 1, delay: 1300 });
    $(".b-seven").transition({ opacity: 1, delay: 500 });
    $(".b-eight").transition({ opacity: 1, delay: 900 });
}
function ani1Out() {
    $(".b-one").transition({ x: '0px', y: '-150px', opacity: 0 });
    $(".b-two").transition({ x: '-100px', y: '0', opacity: 0 });
    $(".b-three").transition({ x: '-100px', y: '0', opacity: 0 });
    $(".b-four").transition({ x: '-100px', y: '0', opacity: 0 });
    $(".b-five").transition({ x: '-100px', y: '0', opacity: 0 });
    $(".b-six").transition({ opacity: 0 });
    $(".b-seven").transition({ opacity: 0 });
    $(".b-eight").transition({ opacity: 0 });
}
function ani2In() {
    $(".a-one").transition({ x: '0px', y: '150px', opacity: 1, delay: 0 });
    $(".a-two").transition({ x: '100px', y: '0', opacity: 1, delay: 100 });
    $(".a-three").transition({ x: '100px', y: '0', opacity: 1, delay: 200 });
    $(".a-four").transition({ x: '100px', y: '0', opacity: 1, delay: 300 });
    $(".a-five").transition({ x: '100px', y: '0', opacity: 1, delay: 400 });
    $(".a-six").transition({ opacity: 1, delay: 1200 });
    $(".a-seven").transition({ x: '-90px', y: '0', opacity: 1, delay: 800 }, 200);
    $(".a-eight").transition({ x: '-90px', y: '0', opacity: 1, delay: 500 }, 200);
}
function ani2Out() {
    $(".a-one").transition({ x: '0px', y: '-150px', opacity: 0 });
    $(".a-two").transition({ x: '-100px', y: '0', opacity: 0 });
    $(".a-three").transition({ x: '-100px', y: '0', opacity: 0 });
    $(".a-four").transition({ x: '-100px', y: '0', opacity: 0 });
    $(".a-five").transition({ x: '-100px', y: '0', opacity: 0 });
    $(".a-six").transition({ opacity: 0 });
    $(".a-seven").transition({ x: '90px', y: '0', opacity: 0 });
    $(".a-eight").transition({ x: '90px', y: '0', opacity: 0 });
}
function ani3In() {
    $(".c-one").transition({ y: '150px', opacity: 1, delay: 0 });
    $(".c-two").transition({ x: '-90px', y: '0', opacity: 1, delay: 100 });
    $(".c-three").transition({ x: '-90px', y: '0', opacity: 1, delay: 200 });
    $(".c-four").transition({ x: '-90px', y: '0', opacity: 1, delay: 300 });
    $(".c-five").transition({ x: '-90px', y: '0', opacity: 1, delay: 400 });
    $(".c-six").transition({ opacity: 1, delay: 1600 });
    $(".c-seven").transition({ x: '200px', y: '0', opacity: 1, delay: 800 }, 200);
    $(".c-eight").transition({ x: '200px', y: '0', opacity: 1, delay: 500 }, 200);
    $(".c-nine").transition({ x: '200px', y: '0', opacity: 1, delay: 1100 }, 200);
}
function ani3Out() {
    $(".c-one").transition({ y: '-150px', opacity: 0 });
    $(".c-two").transition({ x: '90px', opacity: 0 });
    $(".c-three").transition({ x: '90px', opacity: 0 });
    $(".c-four").transition({ x: '90px', opacity: 0 });
    $(".c-five").transition({ x: '90px', opacity: 0 });
    $(".c-six").transition({ opacity: 0 });
    $(".c-seven").transition({ x: '-200px', y: '0', opacity: 0 });
    $(".c-eight").transition({ x: '-200px', y: '0', opacity: 0 });
    $(".c-nine").transition({ x: '-200px', y: '0', opacity: 0 });
}
function ani4In() {
    $(".d-one").transition({ y: '150px', opacity: 1, delay: 0 });
    $(".d-two").transition({ x: '-90px', y: '0', opacity: 1, delay: 100 });
    $(".d-three").transition({ x: '-90px', y: '0', opacity: 1, delay: 200 });
    $(".d-four").transition({ x: '-90px', y: '0', opacity: 1, delay: 300 });
    $(".d-five").transition({ x: '-90px', y: '0', opacity: 1, delay: 400 });
    $(".d-six").transition({ opacity: 1, delay: 1600 });
    $(".d-seven").transition({ x: '200px', y: '0', opacity: 1, delay: 800 }, 200);
    $(".d-eight").transition({ x: '200px', y: '0', opacity: 1, delay: 500 }, 200);
    $(".d-nine").transition({ x: '200px', y: '0', opacity: 1, delay: 1100 }, 200);
}
function ani4Out() {
    $(".d-one").transition({ y: '-150px', opacity: 0 });
    $(".d-two").transition({ x: '90px', opacity: 0 });
    $(".d-three").transition({ x: '90px', opacity: 0 });
    $(".d-four").transition({ x: '90px', opacity: 0 });
    $(".d-five").transition({ x: '90px', opacity: 0 });
    $(".d-six").transition({ opacity: 0 });
    $(".d-seven").transition({ x: '-200px', y: '0', opacity: 0 });
    $(".d-eight").transition({ x: '-200px', y: '0', opacity: 0 });
    $(".d-nine").transition({ x: '-200px', y: '0', opacity: 0 });
}
