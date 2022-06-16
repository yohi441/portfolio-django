document.addEventListener('alpine:init', () => {
    Alpine.store('portfolio', {

        openTab: 1,
        scroll: false,
        scrollEnd: false,
        showAboutCol: false,
        showAboutCol2: false,
        showPortfolioCol1: false,
        showPortfolioCol2: false,
        showPortfolio2Col1: false,
        showPortfolio2Col2: false,
        showPortfolio3Col1: false,
        showPortfolio3Col2: false,
        showContact: false,
        mobileDropdown: false,

        
        scrolled() {
            if (document.documentElement.scrollTop > 20) {
                this.scroll = true 
            }
            else {
                this.scroll = false
                this.showAboutCol = false
                this.showAboutCol2 = false
                this.showPortfolioCol1 =  false
                this.showPortfolioCol2 =  false
                this.showPortfolio2Col1 = false,
                this.showPortfolio2Col2 = false,
                this.showPortfolio3Col1 = false,
                this.showPortfolio3Col2 = false,
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