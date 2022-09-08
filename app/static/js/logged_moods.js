let moods = document.getElementsByClassName("moods")
const [r, g, b] = [57, 59, 87]
const color_dictionary = {
    // each subsequent rgb value is calculated on a pre-selected set of 10 colors
    // ranging from the saddest rgb color to the happiest
    1: [r, g, b],
    2:[r + 19 * 2, g + 17 * 2, b + 8 * 2],
    3:[r + 19 * 3, g + 17 * 3, b + 15 * 3],
    4:[r + 19 * 4, g + 17 * 4, b + 15 * 4],
    5:[r + 19 * 5, g + 17 * 5, b + 15 * 5],
    6:[r + 19 * 6, g + 17 * 6, b + 15 * 6],
    7:[r + 19 * 7, g + 17 * 7, b + 8 * 7],
    8:[r + 19 * 8, g + 17 * 8, b + 8 * 8],
    9:[r + 19 * 9, g + 17 * 9, b + 8 * 9],
    10:[r + 19 * 10, g + 17 * 10, b + 8 * 10],
}

for (let i = 0; i < moods.length; i++)
{
    //console.log(moods[i].getAttribute("value"))
    moods[i].style = `width: 50px; height: 100%; background-color: rgb(${color_dictionary[moods[i].getAttribute("value")][0]}, ${color_dictionary[moods[i].getAttribute("value")][1]}, ${color_dictionary[moods[i].getAttribute("value")][2]}); color: rgb(${color_dictionary[moods[i].getAttribute("value")][0]}, ${color_dictionary[moods[i].getAttribute("value")][1]}, ${color_dictionary[moods[i].getAttribute("value")][2]});`
}