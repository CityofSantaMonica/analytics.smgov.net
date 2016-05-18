module Jekyll
  module FrontMatterJsonify
    # These are keys defined by Jekyll that don't mean anything to analytics-reporter
    JekyllKeys = [
      'next', 'previous', 'path', 'id', 'output', 'content', 'to_s',
      'relative_path', 'url', 'collection', 'excerpt', 'draft', 'categories',
      'title', 'slug', 'ext', 'tags', 'date'
    ]

    def collection_jsonify(collection, ignore_jekyll_keys = false)
      results = []

      collection.each do |item|
        JekyllKeys.each{ |k| item.data.delete(k) } if ignore_jekyll_keys

        results << item.data
      end

      results.to_json
    end
  end
end

Liquid::Template.register_filter(Jekyll::FrontMatterJsonify)