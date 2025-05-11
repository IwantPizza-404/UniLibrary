<template>
    <div>
        <section class="section">
            <div class="container">
                <h1 class="title">404 Not Found</h1>
                <p class="subtitle">
                    The page you are looking for does not exist.
                </p>
            </div>
        </section>
    </div>
</template>

<script>
    export default {
        name: 'NotFound',
        data() {
            return {
                // Add any data properties if needed
            };
        },
        methods: {
            // Add any methods if needed
        },
    }
</script>

<style scoped>
    .section {
        margin-top: 2rem;
        text-align: center;
    }
    .title {
        font-size: 2rem;
        font-weight: 700;
        color: #343a40;
    }
    .subtitle {
        font-size: 1rem;
        color: #6c757d;
    }
</style>