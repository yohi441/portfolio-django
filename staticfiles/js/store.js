document.addEventListener('alpine:init', () => {
    Alpine.store('portfolio', {

        openTab: 1,
        scroll: false,
        scrollEnd: false,
        showAboutCol: false,
        showAboutCol2: false,
        showExp1: false,
        showExp2: false,
        showLearning: false,
        showPortfolioCol1: false,
        showPortfolioCol2: false,
        showPortfolio2Col1: false,
        showPortfolio2Col2: false,
        showPortfolio3Col1: false,
        showPortfolio3Col2: false,
        showPortfolio4Col1: false,
        showPortfolio4Col2: false,
        showPortfolio5Col1: false,
        showPortfolio5Col2: false,
        showPortfolio6Col1: false,
        showPortfolio6Col2: false,
        showPortfolio7Col1: false,
        showPortfolio7Col2: false,
        showPortfolio8Col1: false,
        showPortfolio8Col2: false,
        showPortfolio9Col1: false,
        showPortfolio9Col2: false,
        showContact: false,
        mobileDropdown: false,
        visible: 3,

        
        scrolled() {
            if (document.documentElement.scrollTop > 20) {
                this.scroll = true 
            }
            else {
                this.scroll = false
                this.showAboutCol = false
                this.showAboutCol2 = false
                this.showExp1 = false
                this.showExp2 = false
                this.showLearning = false
                this.showPortfolioCol1 =  false
                this.showPortfolioCol2 =  false
                this.showPortfolio2Col1 = false,
                this.showPortfolio2Col2 = false,
                this.showPortfolio3Col1 = false,
                this.showPortfolio3Col2 = false,
                this.showPortfolio4Col1 = false,
                this.showPortfolio4Col2 = false,
                this.showPortfolio5Col1 = false,
                this.showPortfolio5Col2 = false,
                this.showPortfolio6Col1 = false,
                this.showPortfolio6Col2 = false,
                this.showPortfolio7Col1 = false,
                this.showPortfolio7Col2 = false,
                this.showPortfolio8Col1 = false,
                this.showPortfolio8Col2 = false,
                this.showPortfolio9Col1 = false,
                this.showPortfolio9Col2 = false,
                this.showContact =  false
                        
            }
        },
        scrollToBottom() {
            if ((window.innerHeight + window.scrollY) >= (document.body.offsetHeight-30)) {
                this.scrollEnd = true                                 
            }
            else {
                this.scrollEnd = false
            }
        },
    })
})